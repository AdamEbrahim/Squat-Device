import time
from Utils.config import squat_vars

def file_writer(analysis_file, file_path, name, start_time):
        with open(analysis_file, 'w') as f:
            f.write("File Path: " + file_path + "\n")
            f.write("Squat Analysis: " + str(name) + "\n")
            f.write("Total Reps Attempted: " + str(squat_vars.repCounter + squat_vars.incompleteCounter) + "\n")
            f.write("Completed Reps: " + str(squat_vars.repCounter) + "\n")
            f.write("Incomplete Reps: " + str(squat_vars.incompleteCounter) + "\n")
            f.write("Time to process: " + str(round(time.time() - start_time, 2)) + "s" + "\n")
        f.close()