from hashlib import sha256
# username, hash, [friends list], [public vs. private],
# friends list: [friend1-friend2-friend3-friend4]

# we have: email, firstname, lastname

class User(object):
    def __init__(self,user_data_string):
        self.username, self.hash, self.friends, self.status = self.parseUser(user_data_string)

    def addFriend(self,friendName):
        self.friends.add(friendName)
        return

    def parseUser(self,user_data_string):
    # username, hash, [friends list], [public vs. private],
        [username,passHash,friendsString,status] = user_data_string.split(",")
        friendsList = set(friendsString.split("-"))
        if "" in friendsList:
            friendsList.remove("")
        return username,passHash,friendsList,status

    def __eq__(self,other):
        return type(other) == User and other.username == self.username

    def check_username_password(self, password):
        return sha256(password.encode()).hexdigest() == self.hash

    def makeUserDataStr(self):
        return User.makeDataStr(self.username,self.hash,self.friends,self.status)


    def makeDataStr(username,passhash,friendSet,status):
        friendsString = "-".join(friendSet)
        dataStr = ",".join([username,passhash,friendsString,status])
        return dataStr

    def makeUser(username,password):
        friendSet = {}
        status = "private"
        passhash = sha256(password.encode()).hexdigest()
        return User(User.makeDataStr(username,passhash,friendSet,status))


class LoginData(object):
    def __init__(self,filepath):
        self.filepath = filepath
        self.userList = []
        self.userData = self.loadUserData()

    def loadUserData(self):
        user_data_txt = open(self.filepath, mode="r")
        for user in user_data_txt:
            self.userList.append(User(user))
        return

    def generateUsersFile(self,filepath):
        userDataTXT = open(filepath,"w")
        result = ""
        for user in self.userList:
            result += user.makeUserDataStr()
            # result += "\n"
        userDataTXT.write(result)
        return




if __name__ == "__main__":
    x = LoginData("test.txt")




