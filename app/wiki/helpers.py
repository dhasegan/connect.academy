import reversion

#Performance might be a problem for these two methods
def revert_previous_version(version_list,current_version_in_list):
    revert = False
    for version in version_list:
        if revert:
        	version.revision.revert(delete = True)
        	return revert

        wiki_title = current_version_in_list.field_dict['title']
        wiki_content = current_version_in_list.field_dict['content']

        version_title = version.field_dict['title']
        version_content = version.field_dict['content']
       
        if wiki_title == version_title and wiki_content == version_content:
            revert = True
            continue
    #shouldn't happen
    return False

def find_position_in_version_list(version_list, wiki):
	current_title = wiki.title
	current_content = wiki.content
	for i in range(len(version_list)):
		version_title = version_list[i].field_dict['title']
		version_content = version_list[i].field_dict['content']
		if version_title == current_title and version_content == current_content:
			return i
	#shouldn't happen
	return -1