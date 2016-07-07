class State(object):

    def on_trigger(self, trigger):
        pass

    def _on_trigger(self, trigger):
        log.debug("== " + str(self))
        return self.on_trigger(trigger)

    def on_enter(self, trigger):
        pass

    def _on_enter(self, trigger):
        log.debug("-> " + str(self))
        return self.on_enter(trigger)

    def on_exit(self, trigger):
        pass

    def _on_exit(self, trigger):
        log.debug("<- " + str(self))
        return self.on_exit(trigger)


class Filter(object):

    def __init__(self):
        pass

    def on_process(self, current_state, trigger):
        pass

    def _on_process(self, current_state, trigger):
        log.debug(':: ' + type(self).__name__)
        return self.on_process(current_state, trigger)


class StateMachine(object):

    def __init__(self, user):
        self.state = BootStrapState()
        self.user = user
        self.filters = [StartFilter(),
                        FeedbackFilter(),
                        PoliteFilter()]

    def fire(self, trigger):
        trigger.user = self.user

        for f in self.filters:
            filtered_state = f._on_process(self.state, trigger)
            if filtered_state:
                self.to_state(filtered_state, trigger)
                return

        new_state = self.state._on_trigger(trigger)
        self.to_state(new_state, trigger)

    def to_state(self, new_state, trigger):
        if not new_state:
            return self.state

        if new_state == self.state:
            reenter_state = self.state._on_enter(trigger)
            self.to_state(reenter_state, trigger)
            return

        exit_state = self.state._on_exit(trigger)
        if exit_state:
            self.to_state(exit_state, trigger)
            return

        self.state = new_state

        enter_state = self.state._on_enter(trigger)
        if enter_state:
            self.to_state(enter_state, trigger)
            return


class TelegramTrigger(object):

    def __init__(self):
        self.user = None
        self.bot = None
        self.update = None

    def get_chat_id(self):
        return self.update.message.chat_id if self.update else None

    def get_txt(self):
        return self.update.message.text if self.update else None

    def get_name(self):
        user = self.update.message.from_user
        return user.first_name if user.first_name else user.username

    def send_msg(self, txt):
        self.bot.sendMessage(chat_id=self.chat_id,
                             text=txt,
                             disable_web_page_preview=True,
                             parse_mode=tm.ParseMode.MARKDOWN)

    def send_keys(self, txt, keyboard):
        reply_markup = tm.ReplyKeyboardMarkup(keyboard=keyboard,
                                              resize_keyboard=True,
                                              one_time_keyboard=True)

        self.bot.sendMessage(chat_id=self.chat_id,
                             text=txt,
                             disable_web_page_preview=True,
                             parse_mode=tm.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)

    def send_photo(self, src):
        self.bot.sendPhoto(chat_id=self.chat_id, photo=src)

    # will call 'get_chat_id' when accessing like obj.chat_id
    chat_id = property(get_chat_id)
    txt = property(get_txt)
    name = property(get_name)
