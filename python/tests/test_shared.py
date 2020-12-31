'''
Test module for cross-module logic for running
integration tests for the `yt_videos_list`
package - regardless of the driver
being tested or host operating system.
'''
import os
import sys
import time
import shutil
import hashlib
import datetime
import threading

from determine import determine_path_slash

from yt_videos_list                       import ListCreator


NOW       = datetime.datetime.now
ISOFORMAT = datetime.datetime.isoformat


def log_test_info(message, *args):
    thread_name = f'[{threading.current_thread().name}]'
    message     = f'===>{thread_name:>>14} {message}'
    sys.stdout.writelines(message + '\n')
    for log_file in args:
        with open (log_file, 'a', encoding='utf-8') as output_location:
            output_location.writelines(message + '\n')


class ThreadWithResult(threading.Thread):
    def __init__(self, target, args):
        self.function_to_thread = target
        self.function_arguments = args
        def function():
            self.failed = self.function_to_thread(*self.function_arguments)
        super().__init__(target=function, args=())


def run_tests_for(browsers_list):
    '''
    Runs 2 threads simultaneously to test both
    `reverse_chronological` AND `chronological`
    test cases for every driver in the provided
    `browsers_list`.
    '''
    browsers   = browsers_list
    test_cases = create_test_cases(browsers)
    total      = len(test_cases)
    current    = 0
    log_test_info('*' * 200,                             'CoreySchafer_reverse_chronological_videos_list.log', 'CoreySchafer_chronological_videos_list.log')
    log_test_info(f'{ISOFORMAT(NOW())}: Running tests!', 'CoreySchafer_reverse_chronological_videos_list.log', 'CoreySchafer_chronological_videos_list.log')
    while current < total:
        # each test_case is a ListCreator instance with
        # reverse_chronological set to True or False
        # for EACH driver in the browsers_list,
        # and within EACH test case,
        # there are 5 variations to test - see
        # the list object "variations"
        # in verify_update() for more details
        if threading.active_count() - 1 == 0:
            # the main thread counts as a thread, so we
            # need to subtract 1 to determine the
            # number of threads we've created
            # manually
            thread_1_case      = test_cases[current]
            if getattr(thread_1_case, 'reverse_chronological') is True: log_1_name = 'CoreySchafer_reverse_chronological_videos_list.log'
            else:                                                       log_1_name = 'CoreySchafer_chronological_videos_list.log'
            test_case_thread_1 = ThreadWithResult(target=run_test_case, args=(thread_1_case, log_1_name))
            log_test_info(f'{ISOFORMAT(NOW())}: Starting thread for test case 1...', log_1_name)
            test_case_thread_1.start()
            log_test_info(f'{ISOFORMAT(NOW())}: Started thread for test case 1!', log_1_name)
            current += 1
            # safaridriver does not allow multi-threading:
            # Could not create a session: The Safari instance is already paired with another WebDriver session.
            if 'safari' not in browsers_list:
                if current == 1:
                    # wait 5 seconds to allow all just the firefox selenium webdriver dependency to download (necessary after test_cross_platforms module runs remove_dependencies())
                    time.sleep(5)
                thread_2_case      = test_cases[current]
                if getattr(thread_2_case, 'reverse_chronological') is True: log_2_name = 'CoreySchafer_reverse_chronological_videos_list.log'
                else:                                                       log_2_name = 'CoreySchafer_chronological_videos_list.log'
                test_case_thread_2 = ThreadWithResult(target=run_test_case, args=(thread_2_case, log_2_name))
                log_test_info(f'{ISOFORMAT(NOW())}: Starting thread for test case 2...', log_2_name)
                test_case_thread_2.start()
                log_test_info(f'{ISOFORMAT(NOW())}: Started thread for test case 2!', log_2_name)
                current += 1
        while threading.active_count() - 1 != 0 and current < total:
            # the threads are still running
            time.sleep(7)
        if 'test_case_thread_1' in locals(): test_case_thread_1.join()
        if 'test_case_thread_2' in locals(): test_case_thread_2.join()
        if 'thread_1_case' in locals(): log_test_info(f'{ISOFORMAT(NOW())}: Finished testing {[thread_1_case]}!', log_1_name)
        if 'thread_2_case' in locals(): log_test_info(f'{ISOFORMAT(NOW())}: Finished testing {[thread_2_case]}!', log_2_name)
        if 'test_case_thread_1' in locals() and (getattr(test_case_thread_1, 'failed', None) is None or test_case_thread_1.failed == 'Failed!'): sys.exit()
        if 'test_case_thread_2' in locals() and (getattr(test_case_thread_2, 'failed', None) is None or test_case_thread_2.failed == 'Failed!'): sys.exit()
        test_case_complete = f'{ISOFORMAT(NOW())}: Moving on to the next driver...\n' + '⏬ '*11 + '\n\n\n'
        if   'thread_1_case' in locals() and 'thread_2_case' in locals(): log_test_info(test_case_complete, log_1_name, log_2_name)
        elif 'thread_1_case' in locals():                                 log_test_info(test_case_complete, log_1_name)
        elif 'thread_2_case' in locals():                                 log_test_info(test_case_complete, log_2_name)


def create_test_cases(browsers):
    '''
    Creates an instance of `ListCreator` for a
    reverse chronological AND chronological test case
    for each driver in the provided `browsers` list.
    '''
    return [
        ListCreator(driver=browser, reverse_chronological=is_reverse_chronological)
        for browser in browsers
        for is_reverse_chronological in [True, False]
    ]


def run_test_case(list_creator, log_file):
    '''
    Calls `verify_update()` and `delete_all_schafer5_files()`.
    `verify_update()` runs all variations (no pre-existing files,
    pre-existing txt, pre-existing csv, pre-existing md, and
    pre-existing txt + csv + md files) of the provided test case
    (a specific driver with the `reverse_chronological` attribute
    set to either `True` or `False`) using the
    `list_creator.create_list_for()` method and verifies resulting
    output files match the content in the corresponding full
    reference files. `delete_all_schafer5_files(suffix)` ensures no
    pre-existing files with the corresponding suffix interfere with
    the test and accidentally alter the test results.
    '''
    path_slash               = determine_path_slash()
    schafer5_url             = 'youtube.com/user/schafer5'
    is_reverse_chronological = getattr(list_creator, 'reverse_chronological')
    if is_reverse_chronological: delete_all_schafer5_files('reverse_chronological_videos_list'); return verify_update(list_creator, schafer5_url, f'tests{path_slash}partial_schafer5_reverse_chronological', f'tests{path_slash}full_schafer5_reverse_chronological', log_file)
    else:                        delete_all_schafer5_files('chronological_videos_list');         return verify_update(list_creator, schafer5_url, f'tests{path_slash}partial_schafer5_chronological',         f'tests{path_slash}full_schafer5_chronological', log_file)


def delete_all_schafer5_files(suffix):
    '''
    Deletes all files containing the corresponding suffix to ensure
    tests return valid results not skewed by any pre-existing files.
    The `delete_file(filepath, extension)` helper function deletes
    pre-existing files with the specified extension. The `suffix`
    used to create `filepath` includes
    `reverse_chronological_videos_list` and `chronological_videos_list`
    and the extensions include `txt`, `csv`, and `md`. The prefix in
    all cases is `CoreySchafer_`
    '''
    schafer5 = f'CoreySchafer_{suffix}'
    delete_file(schafer5, 'txt')
    delete_file(schafer5, 'csv')
    delete_file(schafer5, 'md' )


def delete_file(filepath, extension):
    '''
    Removes the file {filepath}.{extension} if it exists.
    '''
    if os.path.exists(f'{filepath}.{extension}'):
        os.remove(f'{filepath}.{extension}')

def verify_update(driver, schafer5_url, test_file, full_file, log_file):
    '''
    Uses the `reverse_chronological` attribute of the `driver`
    argument to determine the suffix, then uses the reference
    `test_file` to create a partial test file. Runs the
    `create_list_for(schafer5_url)` method on the provided
    `driver` instance. Calls
    `compare_test_files_to_reference_files(full_file, file_name)`
    to ensure content in the created output files match the
    content in the full reference files.
    '''
    variations = [
        use_partial_csv_txt_and_md,
        use_no_partial_files,
        use_partial_csv_only,
        use_partial_txt_only,
        use_partial_md_only
        ]
    for create_file in variations:
        is_reverse_chronological = vars   (driver)["reverse_chronological"]
        driver_name              = getattr(driver, 'driver')
        log_test_info(f'{ISOFORMAT(NOW())}: TESTING list_creator with list_creator.reverse_chronological set to {is_reverse_chronological} for {driver_name}driver', log_file)
        if is_reverse_chronological: suffix = 'reverse_chronological_videos_list'
        else:                        suffix = 'chronological_videos_list'
        create_file(test_file, suffix, log_file) # the file this function creates should be the SAME as the returned string to the file_name variable in the next line
        test_output_file = driver.create_list_for(schafer5_url, log_silently=True)
        # verify calling the create_list_for() method updates the partial file properly
        failed = compare_test_files_to_reference_files(full_file, test_output_file, log_file)
        if failed == 'Failed!':
            return 'Failed!'
    return 'Passed!'

def use_no_partial_files(test_file, suffix, log_file):
    '''
    Removes all pre-existing files with the corresponding `suffix`
    (`reverse_chronological_videos_list`
    or
    `chronological_videos_list`;
    the prefix in all cases is `CoreySchafer_`).
    '''
    log_test_info(f'{ISOFORMAT(NOW())}: TESTING with NO pre-existing files AT ALL....\n', log_file)
    delete_all_schafer5_files(suffix)

def use_partial_txt_only(test_file, suffix, log_file):
    '''
    Removes all pre-existing files with the corresponding `suffix`
    (`reverse_chronological_videos_list`
    or
    `chronological_videos_list`;
    the prefix in all cases is `CoreySchafer_`), then creates a
    partial txt file using the `partial_schafer5_{suffix}.txt`
    reference file.
    '''
    log_test_info(f'{ISOFORMAT(NOW())}: TESTING with a pre-existing txt file only (no pre-existing csv or md file)....\n', log_file)
    delete_all_schafer5_files(suffix)
    create_partial_file(test_file, suffix, 'txt')

def use_partial_csv_only(test_file, suffix, log_file):
    '''
    Removes all pre-existing files with the corresponding `suffix`
    (`reverse_chronological_videos_list`
    or
    `chronological_videos_list`;
    the prefix in all cases is `CoreySchafer_`), then creates a
    partial csv file using the `partial_schafer5_{suffix}.csv`
    reference file.
    '''
    log_test_info(f'{ISOFORMAT(NOW())}: TESTING with a pre-existing csv file only (no pre-existing txt or md file)....\n', log_file)
    delete_all_schafer5_files(suffix)
    create_partial_file(test_file, suffix, 'csv')

def use_partial_md_only(test_file, suffix, log_file):
    '''
    Removes all pre-existing files with the corresponding `suffix`
    (`reverse_chronological_videos_list`
    or
    `chronological_videos_list`;
    the prefix in all cases is `CoreySchafer_`), then creates a
    partial md file using the `partial_schafer5_{suffix}.md`
    reference file.
    '''
    log_test_info(f'{ISOFORMAT(NOW())}: TESTING with a pre-existing md file only (no pre-existing txt or csv file)....\n', log_file)
    delete_all_schafer5_files(suffix)
    create_partial_file(test_file, suffix, 'md')

def use_partial_csv_txt_and_md(test_file, suffix, log_file):
    '''
    Removes all pre-existing files with the corresponding `suffix`
    (`reverse_chronological_videos_list`
    or
    `chronological_videos_list`;
    the prefix in all cases is `CoreySchafer_`), then creates
    partial txt, csv, and md files using the
    `partial_schafer5_{suffix}.{ext}` reference files.
    '''
    log_test_info(f'{ISOFORMAT(NOW())}: TESTING with pre-existing txt, csv, and md files....\n', log_file)
    create_partial_file(test_file, suffix, 'txt')
    create_partial_file(test_file, suffix, 'csv')
    create_partial_file(test_file, suffix, 'md' )

def create_partial_file(test_file, suffix, extension):
    '''
    Creates a partial file using `{test_file}.{extension}`
    as the reference file and renames it to
    `CoreySchafer_{suffix}.{extension}`.
    '''
    shutil.copy(f'{test_file}.{extension}', f'CoreySchafer_{suffix}.{extension}')


def compare_test_files_to_reference_files(full_file, test_output_file, log_file):
    '''
    Ensures the resulting test output file `test_output_file`
    contains the exact same content as the reference `full_file` by
    comparing the sha256 hash of both files. If the hashes match,
    the tests continue, but if the hashes don't match, the
    program exits by raising the `SystemExit` exception using
    `sys.exit()`. NOTE that this is insufficient on a
    multi-threaded program since a `SystemExit` exception on one
    thread only terminates THAT thread, and the main thread will
    continue to execute and spin up new threads if there is still
    more work to do. This is a known bug, and will be addressed in
    a future fix.
    '''
    with open(f'{test_output_file}.txt', 'r', encoding='utf-8') as test_txt, open(f'{test_output_file}.csv', 'r', encoding='utf-8') as test_csv, open(f'{test_output_file}.md', 'r', encoding='utf-8') as test_md:
        current_txt = hashlib.sha256(test_txt.read().encode('utf-8')).hexdigest()
        current_csv = hashlib.sha256(test_csv.read().encode('utf-8')).hexdigest()
        current_md  = hashlib.sha256(test_md.read().encode ('utf-8')).hexdigest()
    with open(f'{full_file}.txt', 'r', encoding='utf-8') as full_txt, open(f'{full_file}.csv', 'r', encoding='utf-8') as full_csv, open(f'{full_file}.md', 'r', encoding='utf-8') as full_md:
        verified_txt = hashlib.sha256(full_txt.read().encode('utf-8')).hexdigest()
        verified_csv = hashlib.sha256(full_csv.read().encode('utf-8')).hexdigest()
        verified_md  = hashlib.sha256(full_md.read().encode ('utf-8')).hexdigest()
    failed = False
    if current_txt != verified_txt: log_test_info(f'{ISOFORMAT(NOW())}: ❌ ERROR! The updated txt file does NOT match the {full_file}.txt file!', log_file); failed = True
    else:                           log_test_info(f'{ISOFORMAT(NOW())}: ✅ The updated txt file matches the {full_file}.txt file :)', log_file)
    if current_csv != verified_csv: log_test_info(f'{ISOFORMAT(NOW())}: ❌ ERROR! The updated csv file does NOT match the {full_file}.csv file!', log_file); failed = True
    else:                           log_test_info(f'{ISOFORMAT(NOW())}: ✅ The updated csv file matches the {full_file}.csv file :)', log_file)
    if current_md  != verified_md:  log_test_info(f'{ISOFORMAT(NOW())}: ❌ ERROR! The updated md  file does NOT match the {full_file}.md  file!\n\n\n', log_file); failed = True
    else:                           log_test_info(f'{ISOFORMAT(NOW())}: ✅ The updated md  file matches the {full_file}.md  file :)\n\n\n', log_file)
    if failed:
        log_test_info(f'❗️❗️ FAILED at {ISOFORMAT(NOW())}! ❗️❗️', log_file)
        return 'Failed!'
    return 'Passed!'
