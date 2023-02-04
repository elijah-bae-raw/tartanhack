from hashlib import sha256
from flask import Flask
# username, hash, [friends list], [public vs. private],
# friends list: [friend1-friend2-friend3-friend4]
import random
import smtplib
from email.mime.text import MIMEText
import random



def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()


# a group is made from a list of group members, a limit to the # of group members,
# and location where the group is looking to eat
class Group(object):
    groupCodeChars = list(chr(let) for let in range(97,123))+["1","2","3","4","5","6","7","8","9"]
    groupCodeLength = 6

    def makeGroupCode(self):
        result  = ""
        for ind in range(Group.groupCodeLength):
            result += random.choice(Group.groupCodeChars)
        return result

    def __init__(self,userList,limit,location,private=True): # private groups are invite only
        self.private = private
        self.location = location
        self.members = set()
        self.limit = limit
        self.numMembers = 0
        self.groupCode = self.makeGroupCode()
        for user in userList:
            self.addGroupmember(user)
        return

    def addGroupmember(self,user):
        self.members.add(user)
        user.groupCode = self.groupCode
        self.numMembers+=1
        return

    def updateGroupPrivacy(self,updated):
        self.private = bool(updated)

    def checkGroup(self):
        if self.groupFull():
            self.groupReadyNotifcation()
            self.updateGroupPrivacy(True) # private the group

    def groupFull(self):
        return self.numMembers >= self.limit

    def mergGroups(self,other):
        # assert(isinstance(other,Group))
        allMembers = list(self.members.union(other.member)) # the union of the sets of group members from 2 sets
        newLimit = max(self.limit,other.limit)
        return Group(allMembers,newLimit,self.location)

    def groupReadyNotifcation(self):
        body = "Your lunch group is ready. Here are the details:\n"+str(self)

        for user in self.members:
            subject = f"Hi {user.firstName}, your lunch group is ready!"

            user.notify(subject,body)

    def __str__(self):
        memberString = ""
        for member in self.members:
            memberString += "\n" + "\t\t" + member.firstName
        res =   f'''
    Location: {self.location}
    Members: {memberString}
    Limit: {self.limit}
                '''
        return res

    def __repr__(self):
        return str(self)


# need to keep track of people and groups
class begin(object):
        # uses a dict to keep track of users and of groups
        # groupDict maps groupCode:group
        # users maps User:groupCode
    def __init__(self,data_fp):
        self.filepath = data_fp
        self.emailDict = dict()

        self.users = dict() # self.users is a dict mapping users to the group they are in
        try:
            for user_str in open(data_fp,'r'):
                user_obj = eval(user_str)
                self.users[user_obj] = None
                self.emailDict[user_obj.email] = user_obj
        except FileNotFoundError:
            newFile = open(data_fp,'w')
            self.__init__()

        # self.groupsList = [] # list of group objects (not saved when server down)
        self.groupDict = dict() # a dict mapping group code to group
        return

    def save(self,data_fp=None):
        if data_fp is None:
            data_fp = self.filepath

        saveFile = open(data_fp,"w")

        for user in self.users: # loops over the keys of self.users, which are users
            saveFile.write(repr(user)+"\n")
        return

    # def addUser(self,user): # this is for a set implementation
    #     self.users.add(user)

    def addUser(self,user): # adds an entry into the users dict mapping user to group code
        self.users[user] = user.groupCode
        self.emailDict[user.email] = user

    def addGroup(self,group): # adds an entry in groupDict mapping groupCode to group
        self.groupDict[group.groupCode] = group


# we have: email, firstname, lastname
class User(object):
    def __init__(self,firstName,lastName,email,
                        status="private",bio="",friends=set(),craving=None):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email

        #stuff you don't need for it to be a user
        self.status = status
        self.bio = bio
        self.friends = friends
        self.craving = craving

        self.groupCode = None # group is reset each time the user logs back in
        return

    def notify(self,subject,body):
        sender = "chatgptattartanhack@gmail.com"
        recipients = [self.email]
        appPassword = "clhcpwyaeljzaxhc"
        send_email(subject, body, sender, recipients, appPassword)


    def __repr__(self):
        result = f"User({repr(self.firstName)},{repr(self.lastName)},{repr(self.email)},{repr(self.status)},{repr(self.bio)},{repr(self.friends)},{repr(self.craving)})"
        return result

    def __eq__(self,other):
        return (type(other) == type(self)) and (other.email == self.email)

    def addBio(self,bio):
        self.bio = bio
        return

    def addFriend(self,friend):
        self.friends.add(friend)

    def removeFriend(self,friend):
        if friend in self.friends:
            self.friends.remove(friend)
        return

    def setStatus(self,status):
        self.status = status

    def updateCraving(self,craving):
        self.craving = craving

    def __hash__(self):
        return hash(self.email)






# class User(object):
#     def __init__(self,user_data_string):
#         self.username, self.hash, self.friends, self.status = self.parseUser(user_data_string)

#     def addFriend(self,friendName):
#         self.friends.add(friendName)
#         return

#     def parseUser(self,user_data_string):
#     # username, hash, [friends list], [public vs. private],
#         [username,passHash,friendsString,status] = user_data_string.split(",")
#         friendsList = set(friendsString.split("-"))
#         if "" in friendsList:
#             friendsList.remove("")
#         return username,passHash,friendsList,status

#     def __eq__(self,other):
#         return type(other) == User and other.username == self.username

#     def check_username_password(self, password):
#         return sha256(password.encode()).hexdigest() == self.hash

#     def makeUserDataStr(self):
#         return User.makeDataStr(self.username,self.hash,self.friends,self.status)


#     def makeDataStr(username,passhash,friendSet,status):
#         friendsString = "-".join(friendSet)
#         dataStr = ",".join([username,passhash,friendsString,status])
#         return dataStr

#     def makeUser(username,password):
#         friendSet = {}
#         status = "private"
#         passhash = sha256(password.encode()).hexdigest()
#         return User(User.makeDataStr(username,passhash,friendSet,status))


# class LoginData(object):
#     def __init__(self,filepath):
#         self.filepath = filepath
#         self.userList = []
#         self.userData = self.loadUserData()

#     def loadUserData(self):
#         user_data_txt = open(self.filepath, mode="r")
#         for user in user_data_txt:
#             self.userList.append(User(user))
#         return

#     def generateUsersFile(self,filepath):
#         userDataTXT = open(filepath,"w")
#         result = ""
#         for user in self.userList:
#             result += user.makeUserDataStr()
#             # result += "\n"
#         userDataTXT.write(result)
#         return



# if __name__ == "__main__":
#     x = LoginData("test.txt")




