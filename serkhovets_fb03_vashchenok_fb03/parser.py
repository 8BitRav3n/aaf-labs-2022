"""
Parser file
"""
import re
from core import SQL, Table
from pickle import dump, load

# Settings
file = "MySQL.pickle"
read_file = True
save_file = True

MySQL = SQL()


def load_file():
    global MySQL
    if read_file and file != "":
        try:
            with open(file, 'rb') as f:
                MySQL = load(f)
                return
        except FileNotFoundError:
            pass


def dump_file():
    global MySQL
    if read_file and file != "":
        try:
            with open(file, 'wb') as f:
                dump(MySQL, f)
                return True
        except FileNotFoundError:
            return False


# Init
# MySQL = SQL()
load_file()

tables = re.compile("^[Ss][Hh][Oo][Ww]\s+[Tt][Aa][Bb][Ll][Ee][Ss]\s*;\s*$")
create = re.compile( "^[Cc][Rr][Ee][Aa][Tt][Ee]\s+[a-zA-Z][a-zA-Z0-9_]*\s+\(\s*[a-zA-Z][a-zA-Z0-9_]*(\s*,\s*[a-zA-Z][a-zA-Z0-9_]*)*\s*\)\s*;\s*$")
create_i = re.compile( "^[Cc][Rr][Ee][Aa][Tt][Ee]\s+[a-zA-Z][a-zA-Z0-9_]*\s+\(")
insert = re.compile( "^[Ii][Nn][Ss][Ee][Rr][Tt](\s+[Ii][Nn][Tt][Oo])?\s+[a-zA-Z][a-zA-Z0-9_]*\s+\(\s*\".+\"(\s*, \s*\".+\")*\s*\)\s*;\s*$")
select = re.compile("^[Ss][Ee][Ll][Ee][Cc][Tt]\s+[Ff][Rr][Oo][Mm]\s+[a-zA-Z][a-zA-Z0-9_]*\s*;\s*$")
select_i = re.compile("^[Ss][Ee][Ll][Ee][Cc][Tt]\s+[Ff][Rr][Oo][Mm]\s+[a-zA-Z][a-zA-Z0-9_]* [Ww][Hh][Ee][Rr][Ee]")
save = re.compile("^[Ss][Aa][Vv][Ee];")

pattern_exit = re.compile("^[Ee][Xx][Ii][Tt]\s*;\s*$")

problem_list = ["^[Cc][Rr][Ee][Aa][Tt][Ee]",
                "^[Ii][Nn][Ss][Ee][Rr][Tt]",
                "^[Ss][Ee][Ll][Ee][Cc][Tt]",
                "^[Ee][Xx][Ii][Tt]",
                "^[Ss][Hh][Oo][Ww]"]

pattern_nums = ["[a-zA-Z][a-zA-Z0-9_]*", "(\".+?\")|([a-zA-Z][a-zA-Z0-9_]*)", "[a-zA-Z][a-zA-Z0-9_]*"]

pattern = [create, create_i, insert, select, select_i, tables, save, pattern_exit]


def pattern_sort(post):
    p = post[post.find("WHERE") + 6:].replace(";", "")
    patt_sort = re.compile("([(][(][^(]*[oO][rR][^)]*[)][)])|([(][(][^(]*[aA][nN][dD][^)]*[)][)])")
    temp = re.findall(patt_sort, p)

    temp_post = p

    if not temp:
        return p

    if temp[0][0] == "":
        p = temp[0][1]
    else:
        p = temp[0][0]

    temp_post = temp_post.replace(p, "")

    if "or" in temp_post.lower():
        p += " OR "
    elif "and" in temp_post.lower():
        p += " AND "

    temp_post = temp_post[temp_post.find("("):temp_post.find(")")]
    p += temp_post
    return p


def parsing(command: str):
    for i in range(len(pattern)):
        if pattern[i].match(command):
            # CREATE TABLE
            if i == 0:
                created = re.findall(pattern_nums[0], command)
                MySQL + Table(created[1], created[2:])
                print("You have made changes to the database.")
                return 0
            # CREATE TABLE (INDEXED)
            elif i == 1:
                created = re.findall(pattern_nums[0], command)
                created_dict = {}
                num = 2
                while num < len(created[1:]):
                    if created[num+1] == created[num+1].upper():
                        created_dict[created[num]] = created[num+1]
                        num += 2
                    else:
                        num += 1
                MySQL + Table(created[1], created[2:], created_dict)
                print("You have made changes to the database.")
                return 0
            # CREATE ITEMS
            elif i == 2:
                inserted = re.findall(pattern_nums[1], command)
                if inserted[1][1] == "INTO":
                    inserted = inserted[2:]
                else:
                    inserted = inserted[1:]
                pos = MySQL.get_table(inserted[0][1])
                # print(inserted[1:])
                if pos is not False:
                    newlist = []
                    for item in inserted[1:]:
                        newlist.append(str(item[0]).replace('"', ""))
                        # print(str(item[0]).replace('"', ""))
                    pos.add_items(newlist)
                    print("You have made changes to the database. Rows affected: 1")
                else:
                    print(f"Sorry... no table {inserted[0][1]} :(")
                return 0
            # SELECT table
            elif i == 3:
                selected = re.findall(pattern_nums[2], command)
                print(f"Info from 'SELECT FROM {selected[2]}' :")
                MySQL.print_table(selected[2])
                return 0
            # SELECT table WHERE
            elif i == 4:
                command_sort = pattern_sort(command)
                selected = re.findall(pattern_nums[2], command_sort)
                # print(selected)
                print("Info from 'SELECT':")
                print(re.findall(pattern_nums[2], command)[2], selected,
                                           re.findall(re.compile(">=|<=|=|>|<"), command_sort))
                MySQL.function_print_table(re.findall(pattern_nums[2], command)[2], selected,
                                           re.findall(re.compile(">=|<=|=|>|<"), command_sort))
                return 0
            elif i == 5:
                MySQL.print_tables()
                return 0
            elif i == 6:
                dump_file()
                print(f"Dump database! File {file}")
                return 0
            elif i == 7:
                if save_file:
                    dump_file()
                    print(f"Dump database! File {file}")
                exit("Goodbye! Thank you for your good choice of application! ;)")
            return 0
    if bool(re.match(problem_list[0], command)):
        print("Incorrect 'CREATE' syntax.")
    elif bool(re.match(problem_list[1], command)):
        print("Incorrect 'INSERT' syntax.")
    elif bool(re.match(problem_list[2], command)):
        print("Incorrect 'SELECT' syntax.")
    elif bool(re.match(problem_list[3], command)):
        print("Incorrect 'EXIT' syntax.")
    elif bool(re.match(problem_list[4], command)):
        print("Incorrect 'SHOW' syntax.")
    else:
        print("This command is unfinded:(")


if __name__ == '__main__':
    command = "create t (a, b);"
    created = re.findall(pattern_nums[0], command)
    MySQL + Table(created[1], created[2:])
