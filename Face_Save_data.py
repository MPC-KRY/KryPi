import csv

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    
    return False


def Save_picture_info(id,name,dict):
    if (name.isalpha() and is_number(id)):
        if id == '1':
            fieldnames = ['Name','Ids']
            with open('Profile.csv','w') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(dict)
        else:
            fieldnames = ['Name','Ids']
            with open('Profile.csv','a+') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(dict)