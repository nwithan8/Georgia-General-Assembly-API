# Georgia General Assembly API
A Python library to interact with the Georgia General Assembly website API

*Inspired by [greencracker](https://github.com/greencracker "greencracker"). Major thanks to her [legis.ga.gov API endpoint discovery](https://github.com/greencracker/Georgia_legislature_API_examples)*

# Installation & Setup
1. Add repo and dependencies with `pip install git+https://github.com/nwithan8/Georgia-General-Assembly-API.git zeep`
2. Import the module with `import gga` at the top of your Python script(s)

# Example
```python
import gga

assemby = gga.GeneralAssembly()
legislation = assembly.getLegislationByTypeAndNumber('HB','2')
vote = assembly.getVote(1804)
member = assembly.getMember(179)
session = assembly.sessions['2019-2020 Regular Session']
members = session.getMembers()
legislationItems = session.getLegislationItems()
committees = session.getCommittees()
vote = legislation.getVotes()
committees = legislation.getCommittees()
committeeMember = committees[0].getMembers()[0]
memberName = committeeMember.lastName
cellPhone = committeeMember.district.cellPhone
otherCommitteesForCommitteeMember = committeeMember.getCommittees()
```

# Documentation
## GeneralAssembly()
### Properties:
**sessions**: list of Session objects { [Session, ... ] }

**years**: session years {JSON}

**votes**: list of Vote objects { [Vote, ... ] }

### Methods:
#### getSession():
Get all Georgia General Assembly sessions (run automatically when GeneralAssembly object created, so doesn't need to be manually run)

Returns: list of Session objects { [Session, ... ] }

#### getYears():
Get all Georgia General Assembly years (run automatically when GeneralAssembly object created, so doesn't need to be manually run)

Returns: years (JSON)

#### getVotes():
Get all Georgia General Assembly votes

Returns: list of Vote objects { [Vote, ... ] }

#### getVote(voteId, Session object (optional), Legislation object (optional)):
Get a specific vote
Returns: Vote object {Vote}

#### getMember(int memberId, Session object (optional), Committee object (optional)):
Get a specific member

Returns: Member object {Member}

#### getCommittee(int committeeId, Session object (optional), Member object (optional), Legislation object (optional)):
Get a specific committee

Returns: Committee object {Committee}

#### getLegislation(int legislationId, Session object (optional), Member object (optional), Committee object (optional)):
Get a specific piece of legislation

Returns: Legislation object {Legislation}

#### getCommitteeForSession(int sessionId, int committeeId):
Get a specific committee from a specific session

Returns: Committee object {Committee}

#### getLegislationByTypeAndNumber(string billType, int billNumber):
Get a specific piece of legislation from its bill type and number. Ex. ('HB', 280)

Returns: Legislation object {Legislation}


## Session()
### Properties:
**Id**: ID number {int}

**senateSchedule**: Senate schedule {JSON}

**houseSchedule**: House schedule {JSON}

**members**: dictionary of Member objects { {'Id': Member, ... } }

**legislationItems**: dictionary of Legislation objects { {'Name': Legislation, ... } }

**committees**: dictionary of Committee objects { {'Code': Committee, ... } }

**description**

**library**

**json**: raw data of Session object {JSON}

### Methods:
#### getSchedule(string chamber):
Get the schedule of a specific chamber. Ex. ('House')

Returns: Chamber schedule (JSON)

#### getMembers():
Get the session's members

Returns: dictionary of Member objects  { {'Id': Member, ... } }

#### getLegislationItems():
Get the sessions' pieces of legislation

Returns: dictionary of Legislation objects { {'Name': Legislation, ... } }

#### getCommittees():
Get the sessions' committees

Returns: dictionary of Committee objects { {'Code': Committee, ... } }


## Member()
### Properties:
**Id**: ID number {int}

**session**: Session object {Session}

**currentCommittees**: list of dictionaries of committees member serves on { [{'Code', Committee, 'Role'}, {}, ...] }

**address**: {string}

**birthday**: {string}

**education**: {string}

**firstName**: {string}

**lastName**: {string}

**middleName**: {string}

**nickname**: {string}

**suffix**: {string}

**occupation**: {string}

**religion**: {string}

**spouse**: {string}

**cellPhone**: {int}

**contact**: contact details {Contact}

**biolink**: URL to biography {string}

**comments**: additional comments on member's profile page {string}

**residence**: city of residence {string}

**sessions**: list of sessions the member has served, most recent first { [Session, ...] }

**party**: member's political party {string}

**legId**: {int}

**serviceId**: {int}

**chamber**: what chamber the member served in {string}

**districtNumber**: {int}

**districtId**: {int}

**district**: District object {District}

**title**: {string}

**staff**: staff info {HTML}

**json**: raw data of Member object {JSON}

### Methods:
#### getCommittees(Session object (optional), Committee object (optional)):
Get committees the member serves on

Returns: list of dictionaries of Committee objects { [{'Code', Committee, 'Role'}, {}, ...] }


## Vote()
### Properties:
**Id**: ID number {int}

**session**: Session object {Session}

**day**: day of vote {string}

**time**: time of vote {string}

**datetime**: date and time of vote {datetime}

**number**: vote number {int}

**count**: {'Yeas': ... , 'Nays': ... , 'NotVoting': ... , 'Excused': ... } {JSON}

**result**: result of vote {string}

**chamber**: chamber of the vote {string}

**legislation**: Legislation object {Legislation}

**json**: raw data of Vote object {JSON}


## Legislation()
### Properties:
**Id**: ID number {int}

**session**: Session object {Session}

**votes**: dictionary of votes for the legislation { {'Id': Vote, ...} }

**committees**: list of committees discussing the legislaton { [Committee, ... ] }

**authors**: list of dictionaries of authors of the legislation { [{'Id', Member, 'Type'}, {}, ... ] }

**caption**: {string}

**vetoNumber**: {int}

**documentType**: ex. 'HB' {string}

**type**: {string}

**number**: {int}

**status**: {JSON}

**suffix**: {string}

**footnotes**: {string}

**statusHistory**: {JSON}

**summary**: {string}

**versions**: {JSON}

**votes**: dictionary of votes for the legislation { {'Id': Vote, ... } }

**json**: raw data of Legislation object {JSON}

### Methods:
#### getVotes():
Get votes for the piece of legislation

Returns: dictionary of votes for the legislation { {'Id': Vote, ... } }

#### getCommittees(Session object (optional), Committee object (optional)):
Get committees discussing the legislation

Returns: list of committees discussing the legislaton { [Committee, ... ] }


## Committee():
### Properties:
**Id**: ID number {int}

**session**: Session object {Session}

**members**: list of committee members { [Member, ...] }

**code**: shorthand code for committee {string}

**name**: {string}

**type**: {string}

**description**: {string}

**staff**: {string}

**subcommittees**: {JSON}

**json**: raw data of Committee object {JSON}


### Methods:
#### getMembers(Session object (optional), Member object (optional)):
Get committee members

Returns: list of committee members { [Member, ...] }


## District():
### Properties:
**Id**: ID number {int}

**coverage**: {int}

**post**: {string}

**type**: {string}

**number**: {int}

**json**: raw data of District object {JSON}


## Contact():
### Properties:
**cellPhone**: {int}

**homeNumber**: {int}

**address**: {string}

**city**: {string}

**email**: {string}

**faxNumber**: {int}

**phoneNumber**: {int}

**state**: {string}

**zipCode**: {int}

**json**: raw data of Contact object {JSON}

# Contact
Please leave a pull request if you would like to contribute. There are still a few methods supported by the website's API that (due to lack of documentation), I have not yet deciphered. Feel free to check out greencracker's [Georgia_legislature_API_examples]((https://github.com/greencracker/Georgia_legislature_API_examples) for details and explanation of the website's SOAP API.

Hit me up on Twitter: [@nwithan8](https://twitter.com/nwithan8)

Also feel free to check out my other projects here on [GitHub](https://github.com/nwithan8) or join the #developer channel in my Discord server below.

<div align="center">
	<p>
		<a href="https://discord.gg/ygRDVE9"><img src="https://discordapp.com/api/guilds/472537215457689601/widget.png?style=banner2" alt="" /></a>
	</p>
</div>
