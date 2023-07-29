import time
from Utils.config import squat_vars

def file_writer(analysis_file, start_time, name, file_path=None, date=None):
        with open(analysis_file, 'w') as f:
            if file_path is not None:
                f.write("File Path: " + file_path + "\n")
            elif date is not None:
                f.write("Real Time Processing: " + date + "\n")
            else:
                f.write("Real Time Processing: " + "\n")
            f.write("Squat Analysis: " + str(name) + "\n")
            f.write("Total Reps Attempted: " + str(squat_vars.repCounter + squat_vars.incompleteCounter) + "\n")
            f.write("Completed Reps: " + str(squat_vars.repCounter) + "\n")
            f.write("Incomplete Reps: " + str(squat_vars.incompleteCounter) + "\n")
            if file_path is not None:
                f.write("Time to process: " + str(round(time.time() - start_time, 2)) + "s" + "\n")
            else:
                f.write("Total time: " + str(round(time.time() - start_time, 2)) + "s" + "\n")
            f.write("\n")

            for i in range(len(squat_vars.overallIssues)):
                 for j in range(len(squat_vars.overallIssues[i])):
                      f.write(squat_vars.overallIssues[i][j] + "\n")
