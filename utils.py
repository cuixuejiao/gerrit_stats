import time

def str_time(timestamp):
    """ Convert timestamp to struct time format. """
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    return str_time


def parse_json(dict):
    """ Write change info into parameters config file. """
    # Read json string.
    str_params = {
            'OWNER_NAME': dict['owner']['name'],
            'OWNER_EMAIL': dict['owner']['email'],
            'UPLOADER_NAME': dict['currentPatchSet']['uploader']['name'],
            'UPLOADER_EMAIL': dict['currentPatchSet']['uploader']['email'],
            'CHANGE_KEY': dict['id'],
            'CREATED_ON': str_time(dict['createdOn']),
            'LAST_UPDATED_ON': str_time(dict['lastUpdated']),
            'DEST_PROJECT_NAME': dict['project'],
            'DEST_BRANCH_NAME': dict['branch'],
            'REVISION': dict['currentPatchSet']['revision'],
        }
    num_params = {
            'CURRENT_PATCH_SET_ID': dict['currentPatchSet']['number'],
            'SIZE_INSERTIONS': dict['currentPatchSet']['sizeInsertions'],
            'SIZE_DELETIONS': dict['currentPatchSet']['sizeDeletions'],
        }
    approvals = dict['currentPatchSet']['approvals']
    num = 0
    for approval in approvals:
        str_params['CATEGORY_ID_'+str(num)] = approval['type']
        num_params['VALUE_'+str(num)] = str(approval['value'])
        str_params['GRANTED_'+str(num)] = str_time(approval['grantedOn'])
        str_params['BY_'+str(num)] = approval['by']['name']
        str_params['BY_EMAIL_'+str(num)] = approval['by']['email']
        num += 1
    
    # Write them into params_file.
    params_file = 'params.py'
    with open(params_file, 'w') as f_obj:
        for key, value in sorted(str_params.items()):
            f_obj.write(key + " = '" + value + "'\n")
        for key, value in sorted(num_params.items()):
            f_obj.write(key + " = " + str(value) + "\n")