from __future__ import absolute_import
import gettext
import os, sys
import pytz
import haibot
from telegram import Updater
from telegram.error import TelegramError
from pytz import timezone, utc

from haibot import lists
from haibot import profile
from haibot.terraria import Terraria

try:
    import configparser  # Python 3
except ImportError:
    import ConfigParser as configparser  # Python 2

DEFAULT_LANGUAGE = "en_EN"

def translation_install(translation): # Comnpability with both python 2 / 3
    kwargs = {}
    if sys.version < '3':
        kwargs['unicode'] = True
    translation.install(**kwargs)

def save_user(func):
    def wrapper(self, bot, update, args):
        sender = update.message.from_user
        if not profile.has_user(sender.id):
            try:
                if haibot.config.getint("haibot","BOT_OWNER") == sender.id:
                    is_owner = True
                else:
                    is_owner = False
            except:
                is_owner = False

            user_json = {
            "user_id" : sender.id,
            "user_name" : sender.name,
            "current_list" : "default",
            "in_autonot" : False,
            "is_writer" : is_owner,
            "is_reader" : True,
            "is_terraria_host" : is_owner }

            profile.add_user(user_json)

        return func(self,bot,update,args)
    return wrapper

class HaiBot(object):
    translations = {}
    bot = None

    def __init__(self):
        self.terraria = Terraria()

        #LANGUAGE STUFF
        self.language_list = os.listdir(haibot.config.get("haibot","LOCALE_DIR"))
        for l in self.language_list:
            self.translations[l] = gettext.translation("telegrambot", haibot.config.get("haibot","LOCALE_DIR"), languages=[l], fallback=True)
        try:
            if haibot.config.get("haibot","LANGUAGE") in self.language_list:
                translation_install(self.translations[haibot.config.get("haibot","LANGUAGE")])
            else:
                translation_install(self.translations[DEFAULT_LANGUAGE])
        except:
            translation_install(self.translations[DEFAULT_LANGUAGE])

        # bot INICIALIZATION
        self.updater = Updater(token=haibot.config.get("haibot","TOKEN"))
        self.dispatcher = self.updater.dispatcher
        self.add_handlers()

        # Timezone Stuff
        try:
            self.tzinfo = timezone(haibot.config.get("haibot","TIMEZONE"))
        except:
            self.tzinfo = pytz.utc

    def start_polling_loop(self):
        self.disable_webhook()
        self.update_queue = self.updater.start_polling()
        self.updater.idle()
        self.cleaning()

    def start_webhook_server(self):
        # url/token/server_on |  url/token/server_off | url/token/server_on?hostname |  url/token/server_off?hostname
        from telegram.utils.webhookhandler import WebhookHandler
        from .terraria_server_urls import do_GET
        WebhookHandler.do_GET = do_GET

        self.set_webhook()
        self.update_queue = self.updater.start_webhook(haibot.config.get("haibot","IP"),
                                                       haibot.config.getint("haibot","PORT"),
                                                       haibot.config.get("haibot","TOKEN"))
        self.updater.idle()
        self.cleaning()

    def cleaning(self):
        with open(haibot.CONFIGFILE_PATH, "w") as configfile:
            haibot.config.write(configfile)
            haibot.logger.info("Saving config file...")
        haibot.logger.info("Finished program.")

    def set_webhook(self):
        s = self.updater.bot.setWebhook(haibot.config.get("haibot","WEBHOOK_URL") + "/" + haibot.config.get("haibot","TOKEN"))
        if s:
            haibot.logger.info("webhook setup worked")
        else:
            haibot.logger.warning("webhook setup failed")
        return s

    def disable_webhook(self):
        s = self.updater.bot.setWebhook("")
        if s:
            haibot.logger.info("webhook was disabled")
        else:
            haibot.logger.warning("webhook couldn't be disabled")
        return s

    def add_handlers(self):
        self.dispatcher.addTelegramCommandHandler("start", self.command_start)
        self.dispatcher.addTelegramCommandHandler("help", self.command_help)
        self.dispatcher.addTelegramCommandHandler("terraria", self.command_terraria)
        self.dispatcher.addTelegramCommandHandler("list", self.command_list)
        self.dispatcher.addTelegramCommandHandler("quote", self.command_quote)
        self.dispatcher.addTelegramCommandHandler("search", self.command_search)
        self.dispatcher.addTelegramCommandHandler("settings",self.command_settings)
        self.dispatcher.addTelegramCommandHandler("profile",self.command_profile)
        self.dispatcher.addUnknownTelegramCommandHandler(self.command_unknown)
        #self.dispatcher.addErrorHandler(self.error_handle)
        self.dispatcher.addStringCommandHandler("terraria_on", self.terraria_on)
        self.dispatcher.addStringCommandHandler("terraria_off", self.terraria_off)
        self.dispatcher.addStringCommandHandler("notify", self.notify)

    @save_user
    def command_start(self, bot, update, args):
        self.send_message(bot, update.message.chat_id, _("Bot was initiated. Use /help for commands."))

    @save_user
    def command_help(self, bot, update, args):
        self.send_message(bot, update.message.chat_id, _(
            """Available Commands:
            /start - Iniciciate or Restart the bot
            /help - Show the command list.
            /terraria status/log/autonot/ip - Terraria options
            /list option item - Manage your lists.
            /quote <number>/add/delete/random/search - Save your group chat quotes
            /search engine word - Search using a engine.
            /settings - Change bot options (language, etc.)
            /profile - Show your user profile """))

    @save_user
    def command_terraria(self, bot, update, args):
        chat = update.message.chat_id
        sender = update.message.from_user
        help_text = _(
            """Use one of the following commands:
            /terraria status - Server status (s)
            /terraria log <number> - Show Server history (l)
            /terraria autonot <on/off> - Toogle Autonotifications to user (a)
            /terraria ip - Display server IP (i)
            /terraria milestone - Add a milestone to server (m)
            /terraria on/off manually change server status""")
        if len(args) < 1:
            self.send_message(bot,chat, help_text)
        else:
            if args[0] == "status" or args[0] == "s":
                self.send_message(bot, chat, self.terraria.get_status())

            elif args[0] == "log" or args[0] == "l":
                if len(args) > 1:
                    try:
                        log_text = self.terraria.get_log(int(args[1]), tzinfo=self.tzinfo)
                    except:
                        if args[1] == "m":
                            log_text = self.terraria.get_log(5, only_milestone=True, tzinfo=self.tzinfo)
                        else:
                            log_text = _("/terraria log <number> - Number of log entries to show\n"
                                         "/terraria log m - Show only milestones")
                else:
                    log_text = self.terraria.get_log(5, tzinfo=self.tzinfo)
                if log_text:
                    self.send_message(bot, chat, log_text)
                else:
                    self.send_message(bot, chat, _("There is no Log History"))

            elif args[0] == "autonot" or args[0] == "a":
                if len(args) > 1:
                    if args[1] == "on":
                        profile.set_user_value(sender.id,"in_autonot", True)
                        self.send_message(bot, chat, sender.name+_(" was added to auto notifications."))
                    elif args[1] == "off":
                        profile.set_user_value(sender.id,"in_autonot", False)
                        self.send_message(bot, chat, sender.name+_(" was removed from auto notifications."))
                    else:
                        self.send_message(bot, chat, "/terraria autonot\n/terraria autonot on/off")
                else:
                    if profile.get_user_value(sender.id, "in_autonot"):
                        profile.set_user_value(sender.id,"in_autonot", False)
                        self.send_message(bot, chat, sender.name+_(" was removed from auto notifications."))
                    else:
                        profile.set_user_value(sender.id,"in_autonot", True)
                        self.send_message(bot, chat, sender.name+_(" was added to auto notifications."))


            elif args[0] == "ip" or args[0] == "i":
                self.send_message(bot, chat, self.terraria.get_ip())

            elif args[0] == "milestone" or args[0] == "m":
                if len(args) > 1:
                    milestone_text = self.terraria.add_milestone(sender.name, " ".join(args[1:]))
                    is_confirmated = self.send_message(bot, chat, milestone_text)
                    self.autonotify(milestone_text, check_double=is_confirmated, previous_chat_id=chat)

                else:
                    self.send_message(bot, chat,_("Use /terraria milestone <TEXT>"))

            elif args[0] == "on":
                if len(args) > 1:
                    text = self.terraria.change_status(True, sender.name, args[1])
                else:
                    text = self.terraria.change_status(True, sender.name)
                    self.send_message(bot, chat,_("Note: You can set a IP with:\n/terraria on <your ip>" ))
                is_confirmated = self.send_message(bot, chat, text)
                self.autonotify(text, check_double=is_confirmated, previous_chat_id=chat)

            elif args[0] == "off":
                text = self.terraria.change_status(False, sender.name)
                is_confirmated = self.send_message(bot, chat, text)
                self.autonotify(text, check_double=is_confirmated, previous_chat_id=chat)

            else:
                self.send_message(bot, chat, help_text)

    @save_user
    def command_list(self, bot, update, args):
        chat = update.message.chat_id
        sender = update.message.from_user
        current_list = profile.get_user_value(sender.id,"current_list")
        sender_is_writer = profile.get_user_value(sender.id, "is_writer")
        no_writer_text = _("You have no writting rights")
        no_reader_text = _("You have no reading rights")
        non_existent_list_text = _("Your list do not exists. Select one with \"/list use\"")

        if not profile.get_user_value(sender.id,"is_reader"):
            self.send_message(bot, chat, no_reader_text)
        else:
            help_text = _(
                """Use one of the following commands:
                /list show <all:done:notdone> - show entries in the current list (s)
                /list <number> - Show only one entry using his index
                /list add - add a new entry to the current list (a)
                /list delete - delete an entry from the current list (d)
                /list lists <show:add:delete:clone> - manage lists (l)
                /list use - select a list (makes the list the current list) (u)
                /list writers <show:add:delete> - manage admins for the list (w)
                /list readers <show:add:delete> - manage readers for the list (if apply) (r)
                /list done - mark an entry as <done> (do)
                /list random - pick a random entry and show it (ra)
                /list search - show all entries matching a text (se)""")
            if len(args) < 1:
                self.send_message(bot, chat, help_text)
            else:
                if args[0] == "show" or args[0] == "s":
                    show_help = False
                    if len(args) <2:
                        entry_list = lists.get_entries(current_list,mode="notdone")
                    else:
                        if args[1] == "done" or args[1] == "d":
                            entry_list = lists.get_entries(current_list, mode="done")
                        elif args[1] == "notdone" or args[1] == "n":
                            entry_list = lists.get_entries(current_list, mode="notdone")
                        elif args[1] == "all" or args[1] == "a":
                            entry_list = lists.get_entries(current_list, mode="all")
                        else:
                            show_help = True

                    if show_help:
                        self.send_message(bot, chat, _("Use /list show <all:done:notdone>"))
                    else:
                        if lists.has_list(current_list):
                            if entry_list:
                                entry_text= _("%s: \n") % (current_list)
                                for entry in entry_list:
                                    if entry["done"]:
                                        entry_text += "[%d][done] %s\n" % (entry["index"], entry["entry"] )
                                    else:
                                        entry_text += "[%d] %s\n" % (entry["index"], entry["entry"] )
                                self.send_message(bot, chat, entry_text)
                            else:
                                self.send_message(bot, chat, _("Your list is empty"))
                        else:
                            self.send_message(bot, chat, non_existent_list_text )

                elif args[0] == "add" or args[0] == "a":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list add <name>"))
                    else:
                        if sender_is_writer:
                            new_entry = " ".join(args[1:])
                            if lists.has_list(current_list):
                                new_index = lists.add_entry(new_entry,current_list, sender.name)
                                self.send_message(bot, chat, _("Entry #%d was added to list \"%s\"") % (new_index, current_list))
                            else:
                                self.send_message(bot, chat, non_existent_list_text )
                        else:
                            self.send_message(bot, chat, no_writer_text)

                elif args[0] == "delete" or args[0] == "d":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list delete <entry index>"))
                    else:
                        if sender_is_writer:
                            if lists.has_list(current_list):
                                try:
                                    if lists.has_entry_index(int(args[1]), current_list):
                                        deleted_entry = lists.delete_entry(int(args[1]),current_list)
                                        self.send_message(bot, chat, _("Entry #%d was deleted from list \"%s\".")%(deleted_entry["index"], current_list))
                                    else:
                                        self.send_message(bot, chat, _("The entry number does not exist. Use /list show"))
                                except:
                                    self.send_message(bot, chat, _("Use /list delete <entry number>"))
                            else:
                                self.send_message(bot, chat, non_existent_list_text )
                        else:
                            self.send_message(bot, chat, no_writer_text)

                elif args[0] == "lists" or args[0] == "l":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list lists <show:add:delete:clone>"))
                    else:
                        if args[1] == "show" or args[1] == "s":
                            show_text = ""
                            for list in lists.get_lists(enumerated=True):
                                show_text += "%s: %s\n" % (str(list[0]), list[1])
                            if show_text:
                                self.send_message(bot, chat, show_text)
                            else:
                                self.send_message(bot, chat, _("There is no lists. Create one."))
                        elif args[1] == "add" or args[1] == "a":
                            if len(args) <3:
                                self.send_message(bot, chat, _("/list lists add <something>"))
                            else:
                                if sender_is_writer:
                                    new_list = " ".join(args[2:])
                                    if lists.has_list(new_list):
                                        self.send_message(bot, chat, _("\"%s\" already exists!") % (new_list))
                                    else:
                                        list_index = lists.add_list(new_list, sender.name)
                                        self.send_message(bot, chat, _("\"%s\" list was created. Switch with /list use %d") % (new_list, list_index))
                                else:
                                    self.send_message(bot, chat, no_writer_text)

                        elif args[1] == "delete" or args[1] == "d":
                            if len(args) <3:
                                self.send_message(bot, chat, _("/list lists delete <list index>"))
                            else:
                                if sender_is_writer:
                                    list_array =  lists.get_lists(enumerated=True)
                                    was_deleted = False
                                    for list in list_array:
                                        try:
                                            if list[0] == int(args[2]):
                                                lists.delete_list(list[1])
                                                was_deleted = True
                                                self.send_message(bot, chat,
                                                    _("\"%s\" list was deleted. Use \"show\" for the new order. ")%(list[1]))
                                        except:
                                            was_deleted = False
                                    if not was_deleted:
                                        self.send_message(bot, chat, _("The list could not be deleted. Use:\n"
                                                                                         "/list lists delete <list index>"))
                                else:
                                    self.send_message(bot, chat, no_writer_text)

                        elif args[1] == "clone" or args[1] == "c":
                            self.send_message(bot, chat, _("NOT IMPLEMENTED"))
                        else:
                            self.send_message(bot, chat, _("/list lists <show:add:delete:clone>"))

                elif args[0] == "use" or args[0] == "u":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list use <list ID>\nUse /list lists show for IDs"))
                    else:
                        enumerated_list = lists.get_lists(enumerated=True)
                        is_changed = False
                        for list in enumerated_list:
                            try:
                                if list[0] == int(args[1]):
                                    profile.set_user_value(sender.id, "current_list", list[1])
                                    self.send_message(bot, chat, _("%s selected list: \"%s\"") % (sender.name, list[1]) )
                                    is_changed = True
                            except:
                                is_changed = False
                        if is_changed == False:
                            self.send_message(bot, chat, _("/Invalid ID. Use /list lists show") )

                elif args[0] == "writers" or args[0] == "w":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list writers <show:add:delete:clone>"))
                    else:
                        if args[1] == "show" or args[1] == "s":
                            show_text = ""
                            for list in profile.get_users("is_writer",with_name=True):
                                show_text += "%s: %s\n" % (list["user_id"], list["user_name"])
                            if show_text:
                                self.send_message(bot, chat, show_text)
                            else:
                                self.send_message(bot, chat, _("There is no writers."))
                                haibot.logger.warning("No writers. There should be one. Add bot owner to config file")

                        elif args[1] == "add" or args[1] == "a":
                            add_writers_help = _("/list writer add ID.\n Use \"/profile list\" for a list of known IDs")
                            if len(args) <3:
                                self.send_message(bot, chat, add_writers_help)
                            else:
                                if sender_is_writer:
                                    try:
                                        new_writer = int(args[2])
                                        if profile.has_user(new_writer):
                                            profile.set_user_value(new_writer, "is_writer", True)
                                            self.send_message(bot, chat, _("writer rights for (ID:%d) were added") % (new_writer))
                                        else:
                                            self.send_message(bot, chat, add_writers_help)
                                    except:
                                        self.send_message(bot, chat, add_writers_help)
                                else:
                                    self.send_message(bot, chat, no_writer_text)

                        elif args[1] == "delete" or args[1] == "d":
                            delete_writers_help = _("/list writer delete ID.\n Use \"/list writers show\" for a list of writers IDs")
                            if len(args) <3:
                                self.send_message(bot, chat, delete_writers_help)
                            else:
                                if sender_is_writer:
                                    try:
                                        del_writer = int(args[2])
                                        if profile.has_user(del_writer):
                                            if del_writer != sender.id:
                                                profile.set_user_value(del_writer, "is_writer", False)
                                                self.send_message(bot, chat, _("writer rights for (ID:%d) were deleted") % (del_writer))
                                            else:
                                                self.send_message(bot, chat, _("You can't delete your own rights"))
                                        else:
                                            self.send_message(bot, chat, delete_writers_help)
                                    except:
                                        self.send_message(bot, chat, delete_writers_help)
                                else:
                                    self.send_message(bot, chat, no_writer_text)
                        else:
                            self.send_message(bot, chat, _("/list writers <show:add:delete>"))

                elif args[0] == "readers" or args[0] == "r":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list readers <show:add:delete:clone>"))
                    else:
                        if args[1] == "show" or args[1] == "s":
                            show_text = ""
                            for list in profile.get_users("is_reader",with_name=True):
                                show_text += "%s: %s\n" % (list["user_id"], list["user_name"])
                            if show_text:
                                self.send_message(bot, chat, show_text)
                            else:
                                self.send_message(bot, chat, _("There is no readers."))
                                haibot.logger.warning("No readers. There should be one. Add bot owner to config file")

                        elif args[1] == "add" or args[1] == "a":
                            add_readers_help = _("/list reader add ID.\n Use \"/profile list\" for a list of known IDs")
                            if len(args) <3:
                                self.send_message(bot, chat, add_readers_help)
                            else:
                                if sender_is_writer:
                                    try:
                                        new_reader = int(args[2])
                                        if profile.has_user(new_reader):
                                            profile.set_user_value(new_reader, "is_reader", True)
                                            self.send_message(bot, chat, _("reader rights for (ID:%d) were added") % (new_reader))
                                        else:
                                            self.send_message(bot, chat, add_readers_help)
                                    except:
                                        self.send_message(bot, chat, add_readers_help)
                                else:
                                    self.send_message(bot, chat, no_writer_text)

                        elif args[1] == "delete" or args[1] == "d":
                            delete_readers_help = _("/list reader delete ID.\n Use \"/list readers show\" for a list of readers IDs")
                            if len(args) <3:
                                self.send_message(bot, chat, delete_readers_help)
                            else:
                                if sender_is_writer:
                                    try:
                                        del_reader = int(args[2])
                                        if profile.has_user(del_reader):
                                            if del_reader != sender.id:
                                                profile.set_user_value(del_reader, "is_reader", False)
                                                self.send_message(bot, chat, _("reader rights for (ID:%d) were deleted") % (del_reader))
                                            else:
                                                self.send_message(bot, chat, _("You can't delete your own rights"))
                                        else:
                                            self.send_message(bot, chat, delete_readers_help)
                                    except:
                                        self.send_message(bot, chat, delete_readers_help)
                                else:
                                    self.send_message(bot, chat, no_writer_text)
                        else:
                            self.send_message(bot, chat, _("/list readers <show:add:delete>"))

                elif args[0] == "done" or args[0] == "do":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list done <entry index>"))
                    else:
                        if sender_is_writer:
                            if lists.has_list(current_list):
                                try:
                                    if lists.has_entry_index(int(args[1]), current_list):
                                        entry, done_status = lists.toogle_done_entry(int(args[1]),current_list)
                                        if done_status:
                                            self.send_message(bot, chat,_("#%d: done (list:%s)")%(entry["index"],current_list))
                                            self.send_message(bot, chat,"See: \list show <all:done:notdone>")
                                        else:
                                            self.send_message(bot, chat,_("#%d: notdone (list:%s)")%(entry["index"],current_list))
                                    else:
                                        self.send_message(bot, chat, _("The entry number does not exist. Use /list show all"))
                                except:
                                    self.send_message(bot, chat, _("Use /list done <entry number>"))
                            else:
                                self.send_message(bot, chat, non_existent_list_text )
                        else:
                            self.send_message(bot, chat, no_writer_text)

                elif args[0] == "random" or args[0] == "ra":
                    if lists.has_list(current_list):
                        entry = lists.get_random_entry(current_list)
                        if entry:
                            if entry["done"] == True:
                                self.send_message(bot, chat, "[%d][done] %s\n" % (entry["index"], entry["entry"]))
                            else:
                                self.send_message(bot, chat, "[%d] %s\n" % (entry["index"], entry["entry"]))
                        else:
                            self.send_message(bot, chat, _("Your list is empty"))
                    else:
                        self.send_message(bot, chat, non_existent_list_text )

                elif args[0] == "search" or args[0] == "se":
                    if len(args) <2:
                        self.send_message(bot, chat, _("/list search <words>"))
                    else:
                        if lists.has_list(current_list):
                            result = lists.search_entries(" ".join(args[1:]), current_list)
                            if result:
                                self.send_message(bot, chat, result)
                            else:
                                self.send_message(bot, chat, _("No entries were found"))
                        else:
                            self.send_message(bot, chat, non_existent_list_text )

                else:
                    try:
                        if lists.has_entry_index(int(args[0]), current_list ) :
                            if lists.has_list(current_list):
                                entry = lists.get_entry( int(args[0]), current_list)
                                if entry["done"] == True:
                                    self.send_message(bot, chat, "[%d][done] %s\n" % (entry["index"], entry["entry"]))
                                else:
                                    self.send_message(bot, chat, "[%d] %s\n" % (entry["index"], entry["entry"]))
                            else:
                                self.send_message(bot, chat, non_existent_list_text )
                        else:
                            self.send_message(bot, chat, _("Invalid number. Use /list show o /list search <word>"))
                    except:
                        self.send_message(bot, chat, help_text)

    @save_user
    def command_quote(self, bot, update, args):
        chat = update.message.chat_id
        sender = update.message.from_user

        help_text = _(
            "You can add a quote, selecting a message and clicking on \"reply\" and then writting /quote\n\n"
            "/quote search - show all quotew matching a text (s/se)\n"
            "/quote <number> show the quote associated to a index\n"
            "/quote delete - delete an entry from the current list (d)\n"
            "/quote random - pick a random quote and show it (r/ra)")
        if len(args) < 1:
            if update.message.reply_to_message:
                username = update.message.reply_to_message.from_user.name
                new_quote = update.message.reply_to_message.text
                new_index = lists.add_entry(new_quote, "quote", username)
                if not new_index:
                    self.send_message(bot, chat, _("Error: There is not Quote List in database."))
                    haibot.logger.warning("There is not Quote List in database.")
                else:
                    self.send_message(bot, chat, _("Quote #%d was recorded") % (new_index))
            else:
                self.send_message(bot, chat, help_text)
        else:
            if args[0] == "delete" or args[0] == "d":
                if len(args) <2:
                    self.send_message(bot, chat, _("/quote delete <entry index>"))
                else:
                    if profile.get_user_value(sender.id, "is_writer"):
                        try:
                            if lists.has_entry_index(int(args[1]), "quote"):
                                deleted_entry = lists.delete_entry(int(args[1]), "quote")
                                self.send_message(bot, chat, _("Quote #%d was deleted.")%(deleted_entry["index"]))
                            else:
                                self.send_message(bot, chat, _("The quote number does not exist. Use /quote search <word>"))
                        except:
                            self.send_message(bot, chat, _("Use /quote delete <entry number>"))
                    else:
                        self.send_message(bot, chat, _("You have no writting rights"))

            elif args[0] == "random" or args[0] == "r" or args[0] == "ra" :
                entry = lists.get_random_entry("quote")
                if entry:
                    self.send_message(bot, chat, "*%s*\n`[%d] %s`\n"
                                          % (entry["owner"], entry["index"], entry["entry"]), with_markdown=True)
                else:
                    self.send_message(bot, chat, _("There is no quotes"))

            elif args[0] == "search" or args[0] == "s" or args[0] == "se":
                if len(args) <2:
                    self.send_message(bot, chat, _("/quote search <words>"))
                else:
                    result = lists.search_entries(" ".join(args[1:]), "quote")
                    if result:
                        self.send_message(bot, chat, result)
                    else:
                        self.send_message(bot, chat, _("No quotes were found"))
            else:
                try:
                    if lists.has_entry_index(int(args[0]), "quote" ) :
                        entry = lists.get_entry( int(args[0]), "quote")
                        self.send_message(bot, chat, "*%s*\n`[%d] %s`\n"
                                          % (entry["owner"], entry["index"], entry["entry"]), with_markdown=True)
                    else:
                        self.send_message(bot, chat, _("Invalid number. Use /quote search <word>"))
                except:
                    self.send_message(bot, chat, help_text)

    @save_user
    def command_search(self, bot, update, args):
        self.send_message(bot, update.message.chat_id, _("/search engine word"))

    @save_user
    def command_settings(self, bot,update, args):
        chat = update.message.chat_id
        languages_codes_text = _("Language codes:\n")
        for lang in self.language_list:
            languages_codes_text+= "<"+lang+"> "

        help_text = _("Use /settings language language_code\n\n" + languages_codes_text)

        if len(args) < 2:
            self.send_message(bot, chat, help_text)
        else:
            if args[0] == "language" or args[0] == "l":
                if args[1] in self.language_list:
                    try:
                        haibot.config.set("haibot","LANGUAGE", args[1] )
                        translation_install(self.translations[haibot.config.get("haibot","LANGUAGE")])
                        self.send_message(bot, chat, _("Language changed to %s") % (args[1]))
                        haibot.logger.info("Language was changed to %s" % (args[1]))
                    except:
                        haibot.logger.info("A error happened changing language to %s" % (args[1]))

                else:
                    self.send_message(bot, chat, _("Unknown language code\n\n" + languages_codes_text))
            else:
                self.send_message(bot, chat, help_text)

    @save_user
    def command_profile(self, bot, update,args):
        if len(args) < 1:
            user = profile.get_user(update.message.from_user.id)
            profile_text = ""
            if user:
                for i in user:
                    profile_text += "%s = %s\n" % (str(i), str(user[i]))
            else:
                profile_text = _("Could not get user profile")
        else:
            if args[0] == "list" or args[0] == "l":
                users = profile.get_allusers(projection={"user_id":True, "user_name":True })
                profile_text = ""
                if users:
                    for u in users:
                        profile_text += "%s : %s\n" % (str(u["user_id"]), u["user_name"])
                else:
                    profile_text = _("Could not get profile list")
            else:
                try:
                    profile_id = int(args[0])
                    user = profile.get_user(profile_id)
                    profile_text = ""
                    if user:
                        for i in user:
                            profile_text += "%s = %s\n" % (str(i), str(user[i]))
                    else:
                        profile_text = _("Could not get profile from user <%s>") % (profile_id)
                except:
                        profile_text = _("Use a profile ID with only numbers")

        self.send_message(bot, update.message.chat_id, profile_text)

    @save_user
    def command_unknown(self, bot, update,args):
        self.send_message(bot, update.message.chat_id, _("%s is a unknown command. Use /help for available commands.") % (update.message.text))

    def autonotify(self, text, check_double=False, previous_chat_id=None ):
        autonot_list = profile.get_users("in_autonot")
        for user in autonot_list:
            if check_double and user["user_id"] == previous_chat_id:
                break
            else:
                text_to_queue = str("/notify %s %s" % (user["user_id"], text))
                self.update_queue.put(text_to_queue)

    # /terraria_on IP user
    def terraria_on(self, bot, update, args):
        if len(args) > 1:
            text = self.terraria.change_status(True, " ".join(args[1:]), args[0])
        else:
            text = self.terraria.change_status(True)
        self.autonotify(text)

    # /terraria_of user
    def terraria_off(self, bot, update, args):
        if len(args) > 0:
            text = self.terraria.change_status(False, " ".join(args[0:]))
        else:
            text = self.terraria.change_status(False)
        self.autonotify(text)

    # /notify ID text
    def notify(self, bot, update, args):
        self.send_message(bot, int(args[0]), " ".join(args[1:]))

    def send_message(self, bot, chat_id, text, with_markdown=False):
        try:
            if with_markdown:
                bot.sendMessage(chat_id=chat_id, text=text, disable_web_page_preview=True, parse_mode="Markdown")
            else:
                bot.sendMessage(chat_id=chat_id, text=text, disable_web_page_preview=True)
            return True
        except TelegramError as e:
            try:
                user_name = profile.get_user_value(chat_id, "user_name")
            except:
                user_name = "unknown"
            haibot.logger.warning("A Message could not be sent to User: %s [%d] (TelegramError: %s)" % (user_name, chat_id , e))
            return False
        except:
            haibot.logger.warning("A Message could not be sent:\n%s " % (text))
            return False