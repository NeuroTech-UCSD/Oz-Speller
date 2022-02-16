import datetime
import time
import random

from src.backend_backup import sio

total = ''
stored_index = -1
print('calibration manager initiated -- Start sending trials ...')
# ============= use config instead of hard coding ================
num_trials = 7
trial_duration = 2000
inter_trial_interval = 1000
# ================================================================

characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
              'U', 'V', 'W', 'X', 'Y', 'Z']
stored_values = []
for i in range(num_trials):
    a = datetime.datetime.now()
    random_index = random.randint(0, len(characters) - 1)
    while random_index in stored_values:
        random_index = random.randint(0, len(characters) - 1)
    stored_index = random_index
    stored_values.append(stored_index)
    tic = time.time()
    s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
    print(
        f'calibration manager: send trial {characters[random_index]} to server, time diff since last trial: {time.time() - tic:.3f}, {s}')



print(total)