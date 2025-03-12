# Data Definition # 

## Main Entities ##

### Libary Item: ###
- Items that are held, and can be checked out/etc. at the library
- Attributes:
    - ItemID       Unique identifier for an item.
    - Type         Type of item, i.e. online book, magazine, CD, etc.
    - Title        Title of the item, i.e. "The Great Gatsby"
    - Author       Name of the author, i.e. "F. Scott Gitzgerald"
    - Year         Year of releas, i.e. "2004"
    - Issue        If applicable, issue of release.
    - Location     If physical, where the item is stored
    - Status       If item is reserved, on hold, etc.

- PRIMARY KEY: ItemID


### Member: ###
- Members of the Library
- Attributes:
    - MemberID          Unique member ID, e.g. 3001
    - FirstName         Member first name, e.g. John
    - LastName          Member last name, e.g. Doe
    - PhoneNumber       Member phone number (unique, but may not exist)
    - Email             Member email address (unique, but may not exist)
    - MembershipType    Type of membership (i.e. Gold, Silver, etc.)

- PRIMARY KEY: MemberID


### Personnel: ###
- Staff at the library
- Attributes:
    - PersonnelID      Unique Personnel ID, i.e. 3001
    - Role            Personnel current role, i.e. janitor.
    - Location        Where the Personnel works, i.e. "Burnaby"
    - Salary          What the Personnel currently makes, i.e. 85,000.00 

- PRIMARY KEY: PersonnelID


### Event: ###
- Events held at the library
- Attributes:
    - EventID        Unique ID for event, i.e. 3001
    - EventName      Event name, i.e. "Cocktail night"
    - EventType      Event type, i.e. "Dance"
    - Date           Date of the event, i.e. 03-11-2025
    - AudienceType   Recommendation for specific audience type, i.e. "Mature"
    - Location       Location of the event, i.e. "Burnaby"
    - Room_Number    Room number of the event, i.e. C9001

- PRIMARY KEY: EventID

### FutureItem: ###
- Items that may be added to the library in the future, ISA Item
- Attributes:
    - ItemID            Inherited from Item
    - Title             Title of the item
    - Author            Name of the author of the item
    - Year              Year of release
    - Type              Type of item
    - Issue             Issue details
    - Location          Where the item will be held if physical
    - DateOfArrival     Date when the item will be added if approved
    - ApprovalStatus    Approved/Pending/Denied


## Relationships ##

### Borrows ###
- Relationship to show a customer borrows an item
- Attributes:
    - BorrowID (?)
    - MemberID
    - ItemID
    - BorrowDate
    - DueDate
    - ReturnDate
    - Fine

### Register ###
- Relationship to register a member for an event
- Attributes:
    - EventID     (FK to Event)
    - MemberID    (FK to Member)


### F
