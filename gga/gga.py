import zeep
from zeep import Client

base = 'http://webservices.legis.ga.gov/GGAServices/'
suffix = '/Service.svc?wsdl'

class GeneralAssembly:
    url = base + 'Session' + suffix
    client = Client(url)
    sessions = None
    years = None
    votes = None
    
    def __init__(self):
        self.getSessions()
        self.getYears()
        # To avoid time-consuming calcs at initialization
        #self.getVotes()
        
    def getSessions(self):
        self.sessions = {}
        for s in self.client.service.GetSessions():
            self.sessions[s['Description']] = Session(s['Id'], s)
        return self.sessions
    
    def getYears(self):
        self.years = self.client.service.GetYears()
        return self.years
    
    def getVotes(self):
        self.votes = {}
        for v in Client(base + 'Votes' + suffix).service.GetVotes():
            self.votes[v['VoteId']] = self.getVote(v['VoteId'])
        return self.votes
    
    def getVote(self, Id, session = None, legislation = None):
        return Vote(Id, session, legislation)
    
    def getMember(self, Id, session = None, committee = None):
        return Member(Id, session, committee)
    
    def getCommittee(self, Id, session = None, member = None, legislation = None):
        return Committee(Id, session, member)
    
    def getLegislation(self, Id, session = None, member = None, committee = None):
        return Legislation(Id, session, member, committee)
        
    def getCommitteeForSession(self, sessionId, committeeId):
        session = Session(sessionId)
        return Committee(committeeId, session)
    
    def getLegislationByTypeAndNumber(self, type, number):
        # ex. ('HB', 280)
        data = Client(base + 'Legislation' + suffix).service.GetLegislationDetailByDescription(type, number)
        session = Session(data['Session']['Id'], data['Session'])
        return Legislation(data['Id'], session)

    """
    Currently broken, do not use
    """
    def getMembersByTypeAndSession(self, memberType, sessionId):
        return Client(base + 'Members' + suffix).service.GetMembersByTypeAndSession(memberType, sessionId)
    
    def getCommitteeByTypeAndSession(self, committeeType, sessionId):
        return Client(base + 'Committees' + suffix).service.GetCommitteeByTypeAndSession(committeeType, sessionId)
    
    def getLegislationRanges(self, startIndex, endIndex):
        pass
        
    def getLegislationRange(self, startIndex, endIndex):
        return Client(base + 'Legislation' + suffix).service.GetLegislationRange()
    
    def getLegislationTitles(self):
        return Client(base + 'Legislation' + suffix).service.GetTitles()
    
    def getLegislationSearchResults(self, searchTerm):
        return Client(base + 'Legislation' + suffix).service.GetLegislationSearchResultsPaged(searchTerm)


class Session:
    
    url = base + 'Session' + suffix
    client = Client(url)
    senateSchedule = None
    houseSchedule = None
    members = None
    legislationItems = None
    committees = None
    
    def __init__(self, Id, data = None):
        self.Id = Id
        if data:
            self.description = data['Description']
            self.library = data['Library']
            self.json = data
        # To avoid time-consuming calcs at initialization
        self.getSchedule('House')
        self.getSchedule('Senate')
    
    def getSchedule(self, chamber):
        if chamber == 'House':
            self.houseSchedule = zeep.helpers.serialize_object(self.client.service.GetSessionSchedule(self.Id, chamber))
            return self.houseSchedule
        if chamber == 'Senate':
            self.senateSchedule = zeep.helpers.serialize_object(self.client.service.GetSessionSchedule(self.Id, chamber))
            return self.senateSchedule
        return None
        
    def getMembers(self):
        if not self.members: # members don't change
            self.members = {}
            for m in Client(base + 'Members' + suffix).service.GetMembersBySession(self.Id):
                self.members[m['Id']] = self.getMember(m['Id'], self)
        return self.members
    
    # Internal helper method
    def getMember(self, Id, session = None, committee = None):
        return Member(Id, session, committee)
        
    def getLegislationItems(self):
        self.legislation = {}
        for l in Client(base + 'Legislation' + suffix).service.GetLegislationForSession(self.Id):
            self.legislation[l['Description']] = self.getLegislation(l['Id'], self)
        return self.legislation
    
    # Internal helper method
    def getLegislation(self, Id, session = None, member = None, committee = None):
        return Legislation(Id, session, member, committee)
    
    def getCommittees(self):
        self.committees = {}
        for c in Client(base + 'Committees' + suffix).service.GetCommitteesBySession(self.Id):
            self.committees[c['Code']] = self.getCommittee(c['Id'], self)
        return self.committees
    
    # Internal helper method
    def getCommittee(self, Id, session = None, member = None, legislation = None):
        return Committee(Id, session, member)
    
class Member:
    
    url = base + 'Members' + suffix
    client = Client(url)
    currentCommittees = None
    
    def __init__(self, Id, session = None, committee = None):
        self.Id = Id
        self.session = session
        self.getMember()
    
    # Internal helper method
    def getMember(self, committee = None):
        data = Client(base + 'Members' + suffix).service.GetMember(self.Id)
        self.address = data['Address'] # JSON
        self.birthday = data['Birthday']
        self.education = data['Education']
        self.firstName = data['Name']['First']
        self.lastName = data['Name']['Last']
        self.middleName = data['Name']['Middle']
        self.nickname = data['Name']['Nickname']
        self.suffix = data['Name']['Suffix']
        self.occupation = data['Occupation']
        self.religion = data['Religion']
        self.spouse = data['Spouse']
        self.cellPhone = data['CellPhone']
        self.contact = Contact(data['CellPhone'], data['HomePhone'], data['DistrictAddress'])
        self.bioLink = data['FreeForm1']
        self.comments = data['LegislativeComments']
        self.residence = data['Residence']
        self.sessions = ([self.session] if self.session else [])
        for s in data['SessionsInService']['LegislativeService']:
            if not self.session or s['Session']['Id'] != self.session.Id:
                self.sessions.append(Session(s['Session']['Id'], s['Session']))
        latestSession = data['SessionsInService']['LegislativeService'][0]
        # Historic record of committee membership available in self.json
        self.party = latestSession['Party']
        self.legId = latestSession['LegId']
        self.serviceId = latestSession['ServiceId']
        self.chamber = latestSession['District']['Type']
        self.district = District(latestSession['District'])
        self.districtNumber = latestSession['District']['Number']
        self.districtId = latestSession['District']['Id']
        self.title = latestSession['Title']
        self.staff = data['Staff']
        self.json = data
        
    def getCommittees(self, session = None, committee = None):
        self.currentCommittees = ([committee] if committee else [])
        latestSession = self.json['SessionsInService']['LegislativeService'][0]
        for c in latestSession['CommitteeMemberships']['CommitteeMembership']:
            if not committee or c['Committee']['Id'] != committee.Id:
                tempDict = {'Code': c['Committee']['Code'], 'Committee': self.getCommittee(c['Committee']['Id'], self.session, self), 'Role': c['Role']}
                self.currentCommittees.append(tempDict)
        return self.currentCommittees
            
    # Internal helper method    
    def getCommittee(self, Id, session = None, member = None, legislation = None):
        return Committee(Id, session, member)

class Vote:
    
    url = base + 'Votes' + suffix
    client = Client(url)
    
    def __init__(self, Id, session = None, legislation = None):
        self.Id = Id
        self.session = session
        self.getVote()
     
    # Internal helper method
    def getVote(self, legislation = None):
        data = Client(base + 'Votes' + suffix).service.GetVote(self.Id)
        self.day = data['Day']
        self.time = data['Time']
        self.datetime = data['Date']
        self.number = data['Number']
        self.counts = {
            'Yeas': data['Yeas'],
            'Nays': data['Nays'],
            'NotVoting': data['NotVoting'],
            'Excused': data['Excused']
            }
        self.result = data['Caption']
        self.chamber = data['Branch']
        self.legislation = Legislation()
        self.session = self.session if self.session else Session(data['Session']['Id'], data['Session'])
        self.json = data

class Legislation:
    
    url = base + 'Legislation' + suffix
    client = Client(url)
    votes = None
    session = None
    committees = None
    
    def __init__(self, Id, session = None, member = None, committee = None):
        self.Id = Id
        self.session = session
        self.getLegislation(member, committee)
        # To avoid time-consuming calcs at initialization
        self.getVotes()
    
    # Internal helper method
    def getVotes(self):
        self.votes = {}
        for v in Client(base + 'Votes' + suffix).service.GetVotesForLegislation(self.Id):
            self.votes[v['VoteId']] = self.getVote(v['VoteId'], v, self.session, self)
        return self.votes
    
    # Internal helper method
    def getLegislation(self, member = None, committee = None):
        details = self.client.service.GetLegislationDetail(self.Id)
        self.caption = details['Caption']
        self.vetoNumber = details['ActVetoNumber']
        self.authors = []
        for a in details['Authors']['Sponsorship']:
            tempDict = {'Id': a['MemberId'], 'Member': self.getMember(a['MemberId'], self.session, committee), 'Type': a['Type']}
            self.authors.append(tempDict)
        self.documentType = details['DocumentType']
        #self.latestVersion = details['LastestVersion'] # JSON
        self.type = details['LegislationType']
        self.number = details['Number']
        self.session = self.session if self.session else Session(details['Session']['Id'], details['Session'])
        self.status = details['Status'] # JSON
        self.suffix = details['Suffix']
        self.footnotes = details['Footnotes']
        self.statusHistory = details['StatusHistory'] # Array of JSON
        self.summary = details['Summary']
        self.versions = details['Versions'] # Array of JSON
        self.votes = self.votes if self.votes else self.getVotes()
        self.json = details
        
    def getCommittees(self, session = None, committee = None):
        session = session if session else self.session
        self.committees = ([committee] if committee else [])
        for c in details['Committees']['CommitteeListing']:
            if not committee or c['Id'] != committee.Id:
                self.committees.append(self.getCommittee(c['Id'], self.session, member, self))
        return self.committees
    
    # Internal helper method
    def getVote(self, Id, session = None, legislation = None):
        return Vote(Id, session, legislation)
    
    # Internal helper method
    def getMember(self, Id, session = None, committee = None):
        return Member(Id, session, committee)
    
    # Internal helper method
    def getCommittee(self, Id, session = None, member = None, legislation = None):
        return Committee(Id, session, member)

class Committee:
    
    url = base + 'Committees' + suffix
    client = Client(url)
    members = None
    
    def __init__(self, Id, session = None, member = None, legislation = None):
        self.Id = Id
        self.session = session
        self.getCommittee()
    
    # Internal helper method
    def getCommittee(self, member = None, legislation = None):
        data = self.client.service.GetCommitteeForSession(self.Id, self.session.Id) if self.session else self.client.service.GetCommittee(self.Id)
        self.code = data['Code']
        self.name = data['Name']
        self.type = data['Type']
        self.description = data['Description']
        self.session = self.session if self.session else Session(data['Session']['Id'], data['Session'])
        self.staff = data['Staff']
        self.subcommittees = data['SubCommittees']
        self.json = data
        
    def getMembers(self, session = None, member = None):
        if not self.members: # committee members don't change
            session = session if session else self.session
            self.members = ([member] if member else [])
            for m in self.json['Members']['CommitteeMember']:
                if not member or m['Member']['Id'] != member.Id:
                    self.members.append(self.getMember(m['Member']['Id'], session, self))
        return self.members
    
    # Internal helper method
    def getMember(self, Id, session = None, committee = None):
        return Member(Id, session, committee)

    
class District:
    def __init__(self, district):
        self.coverage = district['Coverage']
        self.post = district['Post']
        self.Id = district['Id']
        self.type = district['Type']
        self.number = district['Number']
        self.json = district

class Contact:
    def __init__(self, cell, home, dist):
        self.cellNumber = cell
        self.homeNumber = home
        self.address = str(dist['Address1']) + (" " + str(dist['Address2']) if dist['Address2'] else "")
        self.city = dist['City']
        self.email = dist['Email']
        self.faxNumber = dist['Fax']
        self.phoneNumber = dist['Phone']
        self.state = dist['State']
        self.zipCode = dist['Zip']
        self.json = dist
        
