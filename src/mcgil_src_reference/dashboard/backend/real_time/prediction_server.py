import socketio
from aiohttp import web
from collections import defaultdict
import itertools

class PredictionServer:

    # finger_name_to_finger_number = {
    #     "left_pinky": 0,
    #     "left_ring": 1,
    #     "left_middle": 2,
    #     "left_index": 3,
    #     "thumb": 4,
    #     "right_index": 5,
    #     "right_middle": 6,
    #     "right_ring": 7,
    #     "right_pinky": 8,
    #     "left_squeeze": 9,
    #     "right_squeeze": 10,
    #     "left_and_right_squeeze": 11
    # }
    
    # maps from finger number to possible finger letters
    # finger_number_to_letters = {
    #     "0": ["q", "a", "z"],
    #     "1": ["w", "s", "x"],
    #     "2": ["e", "d", "c"],
    #     "3": ["r", "f", "v", "t", "g", "b"],
    #     "4": [" "],
    #     "5": ["y", "h", "n", "u", "j", "m"],
    #     "6": ["i", "k", ","],
    #     "7": ["o", "l", "."],
    #     "8": ["p", ";", ":", "'", '"', "/"],
    #     "9": ["0"],
    #     "10": ["\\x7f"],
    #     "11": ["\\x03"]
    # }
    
    finger_name_to_finger_number = {
        "left_pinky": 9,
        "left_ring": 8,
        "left_middle": 7,
        "left_index": 6,
        "thumb": 1,
        "right_index": 2,
        "right_middle": 3,
        "right_ring": 4,
        "right_pinky": 5,
        "left_squeeze": 10,
        "right_squeeze": 11,
        "left_and_right_squeeze": 12
    }
    
    # maps from finger number to possible finger letters
    finger_number_to_letters = {
        "9": ["q", "a", "z"],
        "8": ["w", "s", "x"],
        "7": ["e", "d", "c"],
        "6": ["r", "f", "v", "t", "g", "b"],
        "1": [" "],
        "2": ["y", "h", "n", "u", "j", "m"],
        "3": ["i", "k", ","],
        "4": ["o", "l", "."],
        "5": ["p", ";", ":", "'", '"', "/"],
        "10": ["0"],
        "11": ["\\x7f"],
        "12": ["\\x03"]
    }

    # maps from letter to finger number
    letters_to_finger_numbers = {}
    for number, letters in finger_number_to_letters.items():
        for letter in letters:
            letters_to_finger_numbers[letter] = number

    # create a translator for translating from english to fingers
    english_letters = "qazwsxedcrfvtgbyhnujmikolp"
    # finger_letters = "00011122233333355555566778"
    finger_letters = "99988877766666622222233445"
    english_to_finger_table = "".maketrans(english_letters, finger_letters)

    # translate from english to finger word
    @staticmethod
    def english_to_finger_word(word):
        return word.lower().translate(PredictionServer.english_to_finger_table)

    # build dictionary to translate from fingers to english
    # keys are finger words
    # values are lists of potential english words
    # parameter is a list of common english words
    @staticmethod
    def get_finger_number_to_word_map(word_list):
        word_groupings = defaultdict(list)
        for word in word_list:
            word_groupings[PredictionServer.english_to_finger_word(word)].append(word)
        return word_groupings

    # Data analysis

    # print data on number of conflict counts
    # for words of varying lengths
    @staticmethod
    def get_conflict_counts(word_list):
        word_groupings = defaultdict(list)
        for word in word_list:
            word_groupings[PredictionServer.english_to_finger_word(word)].append(word)

        conflict_count = defaultdict(int)
        for group, words in word_groupings.items():
            group_size = len(words)
            conflict_count[group_size] += 1
            # conflict_count[group_size] += 1

        # for key, val in conflict_count.items():
        #     conflict_count[key] = val * key
        return conflict_count

    # print the top finger words
    @staticmethod
    def calculate_average_word_distance_by_length(word_list, plot_results=False):
        # key: length of finger word
        # value: list of finger words of length key
        finger_word_length_dictionary = defaultdict(list)
        for word in word_list:
            finger_word = PredictionServer.english_to_finger_word(word)
            finger_word_length_dictionary[len(finger_word)].append(finger_word)
            # word_groupings.setdefault(len(finger_word), []).append(finger_word)

        # Function to return the minimum number of
        # operations to convert string A to B
        def minOperations(word1, word2):
            count = 0
            for index, letter in enumerate(word1):
                if letter != word2[index]:
                    count += 1
            return count

        # key: length of finger word
        # value: average min distance of words
        distance_dict = {}
        for length, words in sorted(finger_word_length_dictionary.items()):
            # print(length)
            min_dist_dict = defaultdict(lambda: 100)
            if len(words) > 1:
                for word1, word2 in itertools.combinations((set(words)), 2):
                    min_dist_dict[word1] = min(min_dist_dict[word1], minOperations(word1, word2))
                distance_dict[length] = {
                    "average_min_distance": sum(min_dist_dict.values()) / len(min_dist_dict),
                    "count": len(min_dist_dict)
                }
                # if plot_results:
                #     plt.hist(min_dist_dict.values(), bins=range(length))
                #     plt.show()

        return distance_dict

    def __init__(self, queue, word_groupings, server_mode=False, finger_mode=False):
        self.queue = queue
        self.word_groupings = word_groupings
        self.server_mode = server_mode
        self.finger_mode = finger_mode

        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*", sync_handlers=True)
        self.app = web.Application()
        self.sio.attach(self.app)

    # @staticmethod
    # @sio.event
    # def connect(sid, environ):
    #     print("Client connected", sid)

    # @staticmethod
    # @sio.event
    # def disconnect(sid):
    #     print("Disconnect")

    # gets finger number from prediction algorithm

    async def get_finger_number(self):
        # print("Pulling from queue")
        while self.queue.empty():
            # print("Waiting on empty queue")
            await self.sio.sleep(0.01)

        queueItem = self.queue.get()

        if self.finger_mode:
            # get character prediction
            if self.server_mode:
                for key, value in queueItem.items():
                    # print(key, value)
                    await self.sio.emit(key, {key: value})
                    
            finger_number = str(queueItem["Finger"])

        else:
            # get character from keyboard
            try:
                finger_number = PredictionServer.letters_to_finger_numbers[queueItem]
            except Exception as e:
                print(f"Invalid key: {queueItem}")
                return await self.get_finger_number()

        print(finger_number)
        return finger_number

    # send most likely words
    async def send_most_likely_words(self, words):
        print(words)
        await self.sio.emit('options', {"words": words})

    # trigger word selection mode
    async def send_word_selection_mode(self):
        await self.sio.emit('selection', None)

    # trigger word capture
    async def send_word_capture(self, word):
        await self.sio.emit('word', {"word": word})

    # trigger delete word
    async def send_delete_word(self):
        print("deleting a word")
        await self.sio.emit('delete', None)

    # leave typing mode
    def send_leave_typing_mode(self):
        pass

    # send error code
    def send_error_code(self):
        pass

    # Interactive mode
    # server_mode indicates that we should send messages to the frontend
    async def interactive_mode(self):
        # finger_word stores the word that the user is building
        finger_word = ""

        # sentence stores the words the user has built
        sentence = ""

        async def handle_most_likely_words(potential_words):
            if (len(potential_words) != 0):
                tmp_res = ""
                for index, potential_word in enumerate(potential_words):
                    tmp_res += f"{index}: {potential_word}, "
                print(f"Possible words: {tmp_res}")
            else:
                print("Could not translate")

            if self.server_mode:
                await self.send_most_likely_words(potential_words)

        async def handle_word_selection_mode(potential_words):
            nonlocal finger_word, sentence

            potential_words_display = ""
            for index, potential_word in enumerate(potential_words):
                potential_words_display += f"{index}: {potential_word}, "

            print("Word Selection Mode. Please select a word:")
            print(potential_words_display)

            if self.server_mode:
                await self.send_word_selection_mode()

            finger_number = await self.get_finger_number()

            number = int(finger_number)

            try:
                selected_word = potential_words[number]
            except Exception as e:
                print(f"Key out of selection range: {number}")
                return

            print(f"Selected word: {selected_word}")
            await handle_word_capture(selected_word)

        async def handle_word_capture(english_word):
            nonlocal finger_word, sentence
            finger_word = ""
            sentence += english_word + " "

            print(f"Your Sentence: {sentence}")

            if self.server_mode:
                await self.send_word_capture(english_word)

        async def handle_delete_word():
            nonlocal finger_word, sentence
            sentence = sentence.rsplit(' ', 1)[0]

            if self.server_mode:
                await self.send_delete_word()

        def handle_leave_typing_mode():
            if self.server_mode:
                self.send_leave_typing_mode()
            else:
                exit()

        def handle_error_code(code):
            # add options for continuing or resetting
            if code == "could_not_enter_word_selection_mode":
                print("Could not enter word selection mode. No potential words")

            if self.server_mode:
                self.send_error_code(code)
                
        was_baseline = False
        started = False
                
        # continuously read characters
        while True:
            
            
            finger_number = await self.get_finger_number()
            
            if self.finger_mode:
                if finger_number == "0":
                    was_baseline = True
                elif not was_baseline:
                    print("Skipping")
                    continue
                else:
                    was_baseline = False
                    
            await self.sio.emit('finger', {'number': finger_number})
            
            if not started:
                if finger_number == "1":
                    started = True
                continue
                    
            # type C-c to exit (left and right squeeze)
            # if finger_number == "12":
            if finger_number == "10": # right squeeze, reset finger word
                print("Word reset")
                finger_word = ""
                # handle_leave_typing_mode()

            # type space to select the first word (thumb)
            elif finger_number == "1":
                try:
                    selected_word = self.word_groupings[finger_word][0]
                    await handle_word_capture(selected_word)
                except Exception as e:
                    print(f"No word to select")
                    # finger_word = ""

            # type backspace to go back a character (left squeeze)
            elif finger_number == "11":
                print("Deleting")
                if (len(finger_word) == 0):
                    # remove last word from the sentence
                    await handle_delete_word()
                else:
                    # remove last char from the word
                    finger_word = finger_word[:-1]
                    await handle_most_likely_words(self.word_groupings[finger_word])

            # type 0 to enter word selection mode (left squeeze)
            # elif finger_number == "10":
            elif finger_number == "12": # (left and right squeeze)
                if finger_word in self.word_groupings:
                    await handle_word_selection_mode(self.word_groupings[finger_word])
                else:
                    handle_error_code("could_not_enter_word_selection_mode")

            # other characters are interpretted as typing
            elif finger_number != "0":
                finger_word += finger_number
                print(finger_word)
                await handle_most_likely_words(self.word_groupings[finger_word])

            # print(f"Your Sentence: {sentence}")
            print("")

    def startServer(self):
        self.sio.start_background_task(self.interactive_mode)
        web.run_app(self.app, host='0.0.0.0', port='4002')
