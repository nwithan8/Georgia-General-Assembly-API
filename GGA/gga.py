from typing import Union

from zeep import Client, helpers
from datetime import datetime

base = 'http://webservices.legis.ga.gov/GGAServices/'
suffix = '/Service.svc?wsdl'

def _make_client_url(keyword: str):
    return f"{base}{keyword}{suffix}"

def get_legislation_by_type_and_number(bill_type,
                                       bill_number,
                                       verbose: bool = False):
    # ex. ('HB', 280)
    data = Client(_make_client_url(keyword='Legislation')).service.GetLegislationDetailByDescription(bill_type,
                                                                                                     bill_number)
    return Legislation(legislation_id=data['Id'],
                       session=None,
                       verbose=verbose)

def get_members_by_chamber_and_session(chamber: str, session, raw_data: bool = False):
    if chamber not in ['Senate', 'House']:
        raise Exception("Please indicate 'House' or 'Senate' when getting chamber members.")
    members = []
    data = Client(_make_client_url(keyword='Members')).service.GetMembersByTypeAndSession(
            ('Senator' if chamber == 'Senate' else 'Representative'), session.id)
    if raw_data:
        return data
    for member in data:
        members.append(Member(member_id=member['Id'], session=session))
    return members

"""
    Currently broken, do not use

def getLegislationRanges(startIndex, endIndex):
    pass

def getLegislationRange(startIndex, endIndex):
    return Client(_make_client_url(keyword='Legislation')).service.GetLegislationRange()

def getLegislationSearchResults(searchTerm):
    return Client(_make_client_url(keyword='Legislation')).service.GetLegislationSearchResultsPaged(searchTerm)
"""

class Base:
    def __init__(self, keyword: str = 'Session', verbose: bool = False):
        self.client = Client(_make_client_url(keyword=keyword))
        self.verbose = verbose

    def remake_client(self, keyword: str):
        self.client = Client(_make_client_url(keyword=keyword))

class GeneralAssembly(Base):
    
    def __init__(self, verbose: bool = False):
        super().__init__(keyword='Session',
                         verbose=verbose)
        self._sessions = None
        self._years = None
        self._votes = None

    @property
    def legislation_categories(self):
        categories = []
        for category in Client(_make_client_url(keyword='Legislation')).service.GetTitles():
            categories.append(Category(category_data=category)
                              )
        return categories

    @property
    def sessions(self):
        if not self._sessions:
            self._sessions = self._years_to_sessions()
            """
            self._sessions = []
            for session in self.client.service.GetSessions():
                self._sessions.append(Session(session_id=session['Id'], data=session, verbose=self.verbose))
            """
        return self._sessions

    def get_session(self, session_name: str = None, session_id = None):
        if not session_id and not session_name:
            return None
        for session in self.sessions:
            if session_id and session.id == session_id:
                return session
            elif session_name and session.description == session_name:
                return session
        return None
    
    @property
    def years(self):
        if not self._years:
            self._years = self.client.service.GetYears()
        return self._years

    def _years_to_sessions(self):
        sessions = []
        for year in self.years:
            session_data = year['Session']
            session_data['Year'] = year['Number']
            sessions.append(Session(session_id=session_data['Id'],
                                    data=session_data,
                                    verbose=self.verbose)
                            )
        return sessions
    
    @property
    def votes(self):
        if not self._votes:
            for vote in Client(_make_client_url(keyword='Votes')).service.GetVotes():
                self._votes.append(Vote(vote_id=vote['voteId'],
                                        session=None,
                                        legislation=None,
                                        verbose=self.verbose)
                                   )
        return self._votes

    def reset(self):
        del self._sessions
        del self._years
        del self._votes


class Session(Base):
    
    def __init__(self,
                 session_id,
                 data = None,
                 verbose: bool = False):
        super().__init__(keyword='Session',
                         verbose=verbose)
        self.id = session_id
        self.description = ""
        if data:
            self.description = data['Description']
            self.link = data['Library']
            self.year = data['Year']
            self.json = data

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.description}>"
    
    def get_schedules(self,
                      chamber):
        if chamber not in ['House', 'Senate']:
            raise Exception("Specify either 'House' or 'Senate' when grabbing schedule.")
        schedules = []
        schedule_data = helpers.serialize_object(self.client.service.GetSessionSchedule(self.id, chamber))
        for schedule in schedule_data['Years']['LegislativeYear']:
            schedules.append(Schedule(chamber=chamber,
                                      schedule_data=schedule)
                             )
        return schedules
        
    @property
    def all_members(self):
        members = []
        for member in Client(_make_client_url(keyword='Members')).service.GetMembersBySession(self.id):
            members.append(Member(member_id=member['Id'],
                                  session=self,
                                  verbose=self.verbose)
                           )
        return members

    def get_chamber_members(self, chamber: str):
        return get_members_by_chamber_and_session(chamber=chamber, session=self)

    def get_member(self,
                   member_name: str = None,
                   member_id = None,
                   chamber: str = None):
        if not member_id and not member_name:
            return None
        if chamber:
            members = get_members_by_chamber_and_session(chamber=chamber, session=self, raw_data=True)
        else:
            members = Client(_make_client_url(keyword='Members')).service.GetMembersBySession(self.id)
        for member in members:
            if member_id and member['Id'] == member_id:
                return Member(member_id=member['Id'],
                              session=self,
                              verbose=self.verbose)
            elif member_name and f"{member['Name']['First']} {member['Name']['Last']}" == member_name:
                return Member(member_id=member['Id'],
                              session=self,
                              verbose=self.verbose)
        return None
        
    @property
    def legislation(self):
        legislation = []
        for legis in Client(_make_client_url(keyword='Legislation')).service.GetLegislationForSession(self.id):
            legislation.append(Legislation(legislation_id=legis['Id'],
                                           session=self,
                                           verbose=self.verbose)
                               )
        return legislation
    
    @property
    def committees(self):
        committees = []
        for committee in Client(_make_client_url(keyword='Committees')).service.GetCommitteesBySession(self.id):
            committees.append(Committee(committee_id=committee['Id'],
                                        session=self,
                                        verbose=self.verbose)
                              )
        return committees

    def get_committee(self,
                      committee_id = None,
                      committe_name: str = None):
        if not committee_id and not committe_name:
            return None
        for committee in self.committees:
            if committee_id and committee.id == committee_id:
                return committee
            elif committe_name and committee.name == committe_name:
                return committee
        return None
    
class Member(Base):
    
    def __init__(self,
                 member_id,
                 session: Session,
                 verbose: bool = False,
                 short_data = None,
                 short: bool = False):
        super().__init__(keyword='Members',
                         verbose=verbose)
        self.id = member_id
        if self.verbose:
            print(f"Creating basic {self.__class__.__name__} {self.id}...")
        self.session = session
        self._district = None
        self._contact = None
        self._sessions = []
        if short and short_data:
            self.chamber = ""
            self.name = f"{short_data['Name']['First']} {short_data['Name']['Last']}"
        else:
            self._make_member()

    def expand(self):
        self._make_member()

    def _make_member(self):
        if self.verbose:
            print(f"Expanding {self.__class__.__name__} {self.id}...")
        data = self.client.service.GetMember(self.id)
        self.address = data['Address']
        self.birthday = data['Birthday']
        self.education = data['Education']
        self.firstName = data['Name']['First']
        self.lastName = data['Name']['Last']
        self.middleName = data['Name']['Middle']
        self.nickname = data['Name']['Nickname']
        self.name = f"{self.firstName} {self.lastName}"
        self.suffix = data['Name']['Suffix']
        self.occupation = data['Occupation']
        self.religion = data['Religion']
        self.spouse = data['Spouse']
        self.bioLink = data['FreeForm1']
        self.comments = data['LegislativeComments']
        self.residence = data['Residence']
        self.latestSession = data['SessionsInService']['LegislativeService'][0]
        # Historic record of committee membership available in self.json
        self.party = self.latestSession['Party']
        self.legId = self.latestSession['LegId']
        self.serviceId = self.latestSession['ServiceId']
        self.chamber = self.latestSession['District']['Type']
        self.title = self.latestSession['Title']
        self.staff = data['Staff']
        self.json = data

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.chamber}:{self.name}>"
        
    @property
    def district(self):
        if not self._district:
            self._district = District(district_data=self.latestSession['District'])
        return self._district

    @property
    def contact(self):
        if not self._contact:
            self._contact = Contact(contact_data=self.json)
        return self._contact

    @property
    def sessions(self):
        if not self._sessions:
            for session in self.json['SessionsInService']['LegislativeService']:
                self._sessions.append(Session(session_id=session['Session']['Id']))
        return self._sessions

    @property
    def committees(self):
        committees = []
        for committee in self.latestSession['CommitteeMemberships']['CommitteeMembership']:
            committees.append(Committee(committee_id=committee['Committee']['Id'],
                                        session=self.session,
                                        verbose=self.verbose)
                              )
        return committees

    @property
    def legislation(self):
        legislation = []
        for legis in self.session.legislation:
            for author in legis.authors:
                if author.id == self.id and author.name == self.name:
                    legislation.append(legis)
        return legislation

class Author(Member):
    def __init__(self,
                 author_type,
                 member_id,
                 session: Session,
                 verbose: bool = False,
                 short_data = None,
                 short: bool = False):
        super(Author, self).__init__(member_id=member_id,
                                     session=session,
                                     verbose=verbose,
                                     short_data=short_data,
                                     short=short)
        self.type = author_type

    def __repr__(self):
        return super(Author, self).__repr__()

class District:
    def __init__(self,
                 district_data):
        self.coverage = district_data['Coverage']
        self.post = district_data['Post']
        self.Id = district_data['Id']
        self.type = district_data['Type']
        self.number = district_data['Number']
        self.json = district_data

class Contact:
    def __init__(self,
                 contact_data):
        self.cellNumber = contact_data['CellPhone']
        self.homeNumber = contact_data['HomePhone']
        dist = contact_data['DistrictAddress']
        self.address = f"{dist['Address1']}{' ' + str(dist['Address2']) if dist['Address2'] else ' '}"
        self.city = dist['City']
        self.email = dist['Email']
        self.faxNumber = dist['Fax']
        self.phoneNumber = dist['Phone']
        self.state = dist['State']
        self.zipCode = dist['Zip']
        self.json = contact_data

class Vote(Base):
    
    def __init__(self,
                 vote_id,
                 session: Union[Session, None],
                 legislation,
                 verbose: bool = False):
        super().__init__(keyword='Votes',
                         verbose=verbose)
        self.id = vote_id
        self.session = session
        self._legislation = legislation

        self._make_vote()

    def _make_vote(self):
        if self.verbose:
            print(f"Creating {self.__class__.__name__} {self.id}...")
        data = self.client.service.GetVote(self.id)
        self.day = data['Day']
        self.time = data['Time']
        self.datetime = data['Date']
        self.number = data['Number']
        self.count = VoteCount(vote_count_data=data,
                               vote=self)
        self.result = data['Caption']
        self.chamber = data['Branch']
        self.json = data

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.chamber}:{self.number}>"

class VoteCount:
    def __init__(self,
                 vote_count_data,
                 vote):
        self.yays = vote_count_data['Yeas']
        self.nays = vote_count_data['Nays']
        self.noVotes = vote_count_data['NotVoting'],
        self.excused = vote_count_data['Excused']
        self.vote = vote

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.vote.chamber}:{self.vote.number}:Count>"

class Legislation(Base):

    def __init__(self,
                 legislation_id,
                 session: Union[Session, None],
                 verbose: bool = False):
        super().__init__(keyword='Legislation',
                         verbose=verbose)
        self.id = legislation_id
        self.session = session

        self._make_legislation()

    def _make_legislation(self):
        if self.verbose:
            print(f"Creating {self.__class__.__name__} {self.id}...")
        details = self.client.service.GetLegislationDetail(self.id)
        self.caption = details['Caption']
        self.vetoNumber = details['ActVetoNumber']
        self.documentType = details['DocumentType']
        # self.latestVersion = details['LastestVersion'] # JSON
        self.type = details['LegislationType']
        self.number = details['Number']
        self.status = details['Status']  # JSON
        self.suffix = details['Suffix']
        self.footnotes = details['Footnotes']
        self.statusHistory = details['StatusHistory']  # Array of JSON
        self.summary = details['Summary']
        self.versions = details['Versions']  # Array of JSON
        self.json = details

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.documentType}:{self.number}>"

    @property
    def votes(self):
        votes = []
        for vote in Client(_make_client_url(keyword='Votes')).service.GetVotesForLegislation(self.id):
            votes.append(Vote(vote_id=vote['VoteId'],
                              session=self.session,
                              legislation=self,
                              verbose=self.verbose)
                         )
        return votes

    @property
    def authors(self):
        authors = []
        for author in self.json['Authors']['Sponsorship']:
            authors.append(Author(author_type=author['Type'],
                                  member_id=author['MemberId'],
                                  session=self.session,
                                  verbose=self.verbose)
                                )
        return authors

    @property
    def committees(self):
        committees = []
        for committee in self.json['Committees']['CommitteeListing']:
            committees.append(Committee(committee_id=committee['Id'],
                                        session=self.session,
                                        verbose=self.verbose)
                              )
        return committees

class Committee(Base):
    
    def __init__(self,
                 committee_id,
                 session: Session,
                 verbose: bool = False):
        super().__init__(keyword='Committees',
                         verbose=verbose)
        self.id = committee_id
        self.session = session
        self._members = []

        self._make_committee()

    def _make_committee(self):
        if self.verbose:
            print(f"Creating {self.__class__.__name__} {self.id}...")
        data = self.client.service.GetCommitteeForSession(self.id, self.session.id)
        self.code = data['Code']
        self.name = data['Name']
        self.type = data['Type']
        self.description = data['Description']
        self.staff = data['Staff']
        self.subcommittees = data['SubCommittees']
        self.json = data

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.type}:{self.name}>"

    @property
    def members(self):
        if not self._members:
            for member in self.json['Members']['CommitteeMember']:
                self._members.append(Member(member_id=member['Member']['Id'],
                                            session=self.session,
                                            verbose=self.verbose)
                                     )
        return self._members

class Schedule:
    def __init__(self,
                 chamber,
                 schedule_data):
        self.chamber = chamber
        self.year = schedule_data['Year']
        self.dates = []
        days = schedule_data['Days']['LegislativeDay']
        for day in days:
            self.dates.append(ScheduleDate(date_data=day)
                              )

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.chamber}:{self.year}>"

class ScheduleDate:
    def __init__(self,
                 date_data):
        self._date = date_data['Date']
        self.number = date_data['Number']
        self.chamber = date_data['Branch']

    @property
    def date(self):
        return self._date.strftime("%m-%d-%Y")

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.chamber}:{self.number}:{self.date}>"


class Category:
    def __init__(self, category_data):
        self.code = category_data['Code']
        self.id = category_data['Id']
        self.name = category_data['Name']
        self.parent = category_data['Parent']

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"