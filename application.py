import sqlite3
from datetime import date,timedelta
import time

"""
Resources:

For table formatting:
https://docs.python.org/3/library/string.html#format-specification-mini-language

For general application structure:
https://www.sqlitetutorial.net/sqlite-python/
https://docs.python.org/3/library/sqlite3.html#

For time handling:
https://docs.python.org/3/library/datetime.html

For SQLite3 error handling:
https://docs.python.org/3/library/sqlite3.html#sqlite3-exceptions
"""



def connect_db():
    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    return conn,cur



def find_item(conn,cur):
    # allows the user to search for an item in the library by title, author, or type
    # displays a formatted table
    while True:
        time.sleep(1)
        print("\nFind an item in the library:")
        print("Type EXIT() to exit the search")
        keywords=input("Enter keywords: ").strip()
        if keywords.upper()=="EXIT()":
            break

        if keywords=="":
            print("No keywords entered, please try again")
            continue

        cur.execute("SELECT itemID,title,author,itemType,itemStatus FROM LibraryItem WHERE title LIKE ? OR author LIKE ? OR itemType LIKE ?",(f'%{keywords}%',f'%{keywords}%',f'%{keywords}%'))
        results=cur.fetchall()
        if results:

            print("Items found:")
            print(f"{'ID':<4} {'Title':<30} {'Author':<20} {'Type':<15} {'Status':<12}")
            print("-"*80)
            for row in results:
                print(f"{row[0]:<4} {row[1]:<30} {row[2] or 'N/A':<20} {row[3] or 'N/A':<15} {row[4] or 'N/A':<12}")
        else:
            print("No items found with your search criteria")



def show_available_items(cur,limit=5):
    # helper function to show available items in the library
    cur.execute("SELECT itemID,title,author FROM LibraryItem WHERE itemStatus='Available' ORDER BY itemID LIMIT ?",(limit,))
    rows=cur.fetchall()

    if rows:
        print(f"\nAvailable Items (up to {limit}):")
        print(f"{'ID':<4} {'Title':<30} {'Author':<20}")
        print("-"*60)
        for r in rows:
            print(f"{r[0]:<4} {r[1] or 'N/A':<30} {r[2] or 'N/A':<20}")
    else:
        print("\nNo items available at the moment")



def borrow_item(conn,cur,member_id):
    # allows the user to borrow an item from the library
    # displays a formatted table of available items
    while True:
        time.sleep(1)
        print("\nBorrow an item from the library:")
        print("Type EXIT() to exit this operation")
        show_available_items(cur,limit=5)

        item_input=input("Enter the ID of the item to borrow: ").strip()
        if item_input.upper()=="EXIT()":
            print("Returning to main menu...")
            break

        if not item_input.isdigit():
            print("Invalid input, ID must be numeric")
            continue

        item_id=int(item_input)
        cur.execute("SELECT itemStatus FROM LibraryItem WHERE itemID=?", (item_id,))
        row=cur.fetchone()

        if not row:
            print("No item found with that ID")
            continue

        if row[0]!="Available":
            print(f"Item {item_id} is not available (Status: {row[0]})")
            continue

        # due date is 14 days from today automatically    
        today=date.today()
        due=today+timedelta(days=14)
        
        try:
            cur.execute("INSERT INTO Borrows (itemID,memberID,borrowDate,dueDate) VALUES (?,?,?,?)",(item_id,member_id,today.isoformat(),due.isoformat()))
            conn.commit()
            print("Item borrowed successfully!")
            print(f"Borrowed on: {today.isoformat()}")
            print(f"Due date:    {due.isoformat()}")
            break

        except sqlite3.IntegrityError as e:
            # TODO: change
            print("This item is already borrowed by you or another member")
            #print(f"DEBUG: {e}")
            continue

        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
            continue



def return_item(cur,conn,member_id):
    # allows the user to return an item to the library
    print("\nYour borrowed (unreturned) items:")
    cur.execute("SELECT B.itemID,L.title,L.author,B.borrowDate,B.dueDate FROM Borrows B JOIN LibraryItem L ON B.itemID=L.itemID WHERE B.memberID=? AND B.returnDate IS NULL",(member_id,))
    items=cur.fetchall()

    if not items:
        print("You have no items to return")
        return
    
    print(f"{'ID':<4} {'Title':<30} {'Author':<20} {'Borrowed':<12} {'Due':<12}")
    print("-"*80)

    for item in items:
        print(f"{item[0] or 'N/A':<4} {item[1] or 'N/A':<30} {item[2] or 'N/A':<20} {item[3] or 'N/A':<12} {item[4] or 'N/A':<12}")
    
    while True:
        time.sleep(1)
        print("\nEnter the ID of the item to return (or type EXIT() to cancel):")
        item_input=input("Item ID: ").strip()
        if item_input.upper()=="EXIT()":
            print("Return process cancelled")
            break

        if not item_input.isdigit():
            print("Invalid input. Enter a valid numeric item ID")
            continue

        item_id=int(item_input)
        return_date=date.today().isoformat()
        try:
            cur.execute("UPDATE Borrows SET returnDate=? WHERE itemID=? AND memberID=? AND returnDate IS NULL",(return_date,item_id,member_id))
            if cur.rowcount==0:
                print("That item is not borrowed by you or already returned")
            else:
                conn.commit()
                print(f"Item {item_id} returned on {return_date}")
            break

        except sqlite3.Error as e:
            print(f"unknown error: {e}, file a helpRequest")
            break




def donate_item(conn,cur):
    # allows the user to donate an item to the library
    while True:
        print("\nDonate an item to the library:")
        
        title=input("Enter the title (or type EXIT() to cancel): ").strip()
        if title.upper()=="EXIT()":
            print("Donation cancelled")
            return
        
        author=input("Enter the author: ").strip()
        item_type=input("Enter the type (e.g., Book, DVD): ").strip()
        year_input=input("Enter the year of publication: ").strip()

        try:
            year=int(year_input)
        except:
            print("Invalid year input")
            continue
        
        issue=input("Enter the issue number if applicable (or type EXIT() to cancel): ").strip()
        
        issue_num=None
        if issue:
            try:
                issue_num=int(issue)
            except:
                print("Invalid issue number.")
                continue
            
        cur.execute("INSERT INTO LibraryItem (title,author,itemType,releaseYear,issueNumber) VALUES (?,?,?,?,?)",(title,author,item_type,year,issue_num))
        item_id=cur.lastrowid
        conn.commit()

        print("Item donated successfully!")
        print(f"Item ID: {item_id}")

        print("Thank you for your donation!")
        break




def find_event(conn,cur):
    # allows the user to search for an event in the library by name, type, or audience type
    keywords=input("Enter keywords to search for an event (or type EXIT() to cancel): ").strip()
    if keywords.upper()=="EXIT()":
        print("Search canceled")
        return
    
    cur.execute("SELECT eventID,eventName,eventType,eventDate,audienceType FROM Event WHERE eventName LIKE ? OR eventType LIKE ? OR audienceType LIKE ?",(f'%{keywords}%',f'%{keywords}%',f'%{keywords}%'))
    results=cur.fetchall()
    if not results:
        print("No events found")
        return
    
    print("Events Matching Your Search:")
    print(f"{'ID':<4} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10}")
    print("-"*70)

    for result in results:
        event_id,name,etype,edate,audience=result
        print(f"{event_id or 'N/A':<4} {name or 'N/A':<25} {etype or 'N/A':<15} {edate or 'N/A':<12} {audience or 'N/A':<10}")
    print()



def show_available_events(conn,cur,limit=5):
    # helper function to show available events in the library
    cur.execute("SELECT eventID,eventName,eventType,eventDate,audienceType FROM Event ORDER BY eventID LIMIT ?",(limit,))
    rows=cur.fetchall()
    if rows:
        print(f"\nAvailable Events (up to {limit}):")
        print(f"{'ID':<4} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10}")
        print("-"*70)
        for r in rows:
            print(f"{r[0] or 'N/A':<4} {r[1] or 'N/A':<25} {r[2] or 'N/A':<15} {r[3] or 'N/A':<12} {r[4] or 'N/A':<10}")
    else:
        print("\nNo events available at the moment.")



def show_signed_up_events(conn,cur,member_id):
    # helper function to show events the user is registered for based on member id
    # displays a formatted table
    cur.execute("SELECT E.eventID,E.eventName,E.eventType,E.eventDate,E.audienceType FROM Register R JOIN Event E ON R.eventID=E.eventID WHERE R.memberID=?",(member_id,))
    rows=cur.fetchall()
    if rows:
        print("\nEvents You Are Registered For:")
        print(f"{'ID':<4} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10}")
        print("-"*70)

        for r in rows:
            print(f"{r[0] or 'N/A':<4} {r[1] or 'N/A':<25} {r[2] or 'N/A':<15} {r[3] or 'N/A':<12} {r[4] or 'N/A':<10}")
    else:
        print("\nYou are not registered for any events at this time")



def register_for_event(conn,cur,member_id):
    # lts user sign up for event
    while True:
        print("\nRegister for an event:")
        show_signed_up_events(conn,cur,member_id)
        show_available_events(conn,cur)
        event_id=input("Enter the ID of the event to register for (or type EXIT() to cancel): ").strip()
        if event_id.upper()=="EXIT()":
            print("Registration cancelled.")
            break
        
        if not event_id.isdigit():
            print("ID should be numeric")
            continue
        
        try:
            event_id=int(event_id)
            cur.execute("INSERT INTO Register (memberID,eventID) VALUES (?,?)",(member_id,event_id))
            conn.commit()
            print("Registration successful!")
            print(f"Registered for event ID {event_id}.")
            break

        except sqlite3.IntegrityError as e:
            print("You are already registered for this event")
            #print(f"DEBUG: {e}")
            continue
        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}, if this is unexpected please file a help request")
            break



def print_available_jobs(conn,cur):
    # helper function to show available volunteering positions in the library
    cur.execute("SELECT positionID,positionName,positionDescription,location,isAvailable FROM VolunteeringPositions WHERE isAvailable=1 ORDER BY positionID")
    rows=cur.fetchall()

    if not rows:
        print("No positions at the moment")
        return
    print("Available Volunteering Positions:")

    print(f"{'ID':<4} {'Position Name':<25} {'Location':<20}")

    print("-"*60)
    for row in rows:
        print(f"{row[0] or 'N/A':<4} {row[1] or 'N/A':<25} {row[3] or 'N/A':<20}")
        if row[2]:
            print(f"Description: {row[2]}")
        print()



def print_current_volunteering_positions(conn,cur,member_id):
    # helper function to show current volunteering positions the user is registered for based on member id
    cur.execute("SELECT V.positionID,P.positionName,P.positionDescription,P.location FROM Volunteer V JOIN VolunteeringPositions P ON V.positionID=P.positionID WHERE V.memberID=?",(member_id,))
    rows=cur.fetchall()

    if not rows:
        print("You are not registered for any volunteering")
        return
    
    print("Your Volunteering Positions:")
    print(f"{'ID':<4} {'Position Name':<25} {'Location':<20}")
    print("-"*60)
    for row in rows:
        print(f"{row[0] or 'N/A':<4} {row[1] or 'N/A':<25} {row[3] or 'N/A':<20}")
        if row[2]:
            print(f"Description: {row[2]}")
        print()



def volunteer(conn,cur,member_id):
    while True:
        print("\nVolunteer for the library:")
        print_current_volunteering_positions(conn,cur,member_id)
        print_available_jobs(conn,cur)

        positionid=input("Enter the ID of the position to volunteer for (or type EXIT() to cancel): ").strip()
        if positionid.upper()=="EXIT()":
            print("Volunteer process cancelled")
            break
        
        if not positionid.isdigit():
            print("ID should be numeric")
            continue
        
        positionid=int(positionid)
        cur.execute("SELECT isAvailable FROM VolunteeringPositions WHERE positionID=?",(positionid,))
        row=cur.fetchone()

        if not row:
            print("No position found with that ID")
            continue
        
        if row[0]==0:
            print(f"Position {positionid} is not available.")
            break
        
        try:
            cur.execute("INSERT INTO Volunteer (memberID,positionID) VALUES (?,?)",(member_id,positionid))
            cur.execute("UPDATE VolunteeringPositions SET isAvailable=0 WHERE positionID=?",(positionid,))
            conn.commit()
            print("Volunteer registration successful!")
            print(f"Registered for position ID {positionid}.")
            break

        except sqlite3.IntegrityError as e:
            print("You are already registered for this position.")
            #print(f"DEBUG: {e}")
            continue

        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
            break



def request_help(conn,cur,member_id):
    print("\nAsk a librarian for help:")
    print("Type EXIT() to exit this operation")

    while True:
        topic=input("Describe the topic you need help with: ").strip()
        if topic.upper()=="EXIT()":
            print("Help request cancelled.")
            return
        
        if not topic:
            print("Topic cannot be empty.")
            continue

        today=date.today().isoformat()

        try:
            cur.execute("INSERT INTO HelpRequest (memberID,requestDate,topic) VALUES (?,?,?)",(member_id,today,topic))
            conn.commit()
            print("Help request submitted successfully!")
            print(f"Request Date: {today}")
            print(f"Topic: {topic}")
            break
    
        except sqlite3.IntegrityError as e:
            print("Unable to submit help request, please try again")
            #print(f"DEBUG: {e}")

        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
            return



def view_all_members(conn,cur):
    print("\nAll Members:")
    cur.execute("SELECT memberID,firstName,lastName,email,phoneNumber,membershipType FROM Member")

    rows=cur.fetchall()
    if not rows:
        print("No members found")
        return
    
    print(f"{'ID':<4} {'Name':<30} {'Email':<25} {'Phone':<15}")
    print("-"*80)
    for row in rows:
        print(f"{row[0] or 'N/A':<4} {row[1]+' '+row[2]:<30} {row[3] or 'N/A':<25} {row[4] or 'N/A':<15}")
        print()



def view_all_borrowed_items(conn,cur):
    print("\nCurrently Borrowed Items:")
    cur.execute("SELECT B.itemID,L.title,M.firstName||' '||M.lastName,B.borrowDate,B.dueDate FROM Borrows B JOIN LibraryItem L ON B.itemID=L.itemID JOIN Member M ON B.memberID=M.memberID")
    rows=cur.fetchall()

    if not rows:
        print("No items are currently borrowed.")
        return
    
    print(f"{'Item ID':<8} {'Title':<30} {'Borrower':<25} {'Borrowed':<12} {'Due':<12}")
    print("-"*90)
    for row in rows:
        print(f"{row[0]:<8} {row[1]:<30} {row[2] or 'N/A':<25} {row[3] or 'N/A':<12} {row[4] or 'N/A':<12}")
        print()



def view_all_volunteers(conn,cur):
    print("\nCurrently Registered Volunteers:")
    cur.execute("SELECT V.memberID,M.firstName||' '||M.lastName,P.positionName,P.location FROM Volunteer V JOIN Member M ON V.memberID=M.memberID JOIN VolunteeringPositions P ON V.positionID=P.positionID")
    rows= cur.fetchall()

    if not rows:
        print("No volunteers found.")
        return
    
    print(f"{'Member ID':<10} {'Name':<30} {'Position':<25} {'Location':<20}")
    print("-"*90)
    for row in rows:
        print(f"{row[0]:<10} {row[1] or 'N/A':<30} {row[2] or 'N/A':<25} {row[3] or 'N/A':<20}")
        print()



def view_all_help_requests(conn,cur):
    print("\nAll Help Requests:")
    cur.execute("SELECT H.requestID,M.firstName||' '||M.lastName,H.requestDate,H.topic FROM HelpRequest H JOIN Member M ON H.memberID=M.memberID ORDER BY H.requestDate DESC")
    rows=cur.fetchall()

    if not rows:
        print("No help requests found.")
        return
    
    print(f"{'Request ID':<10} {'Member Name':<30} {'Date':<12} {'Topic':<40}")
    print("-"*100)
    for row in rows:
        print(f"{row[0]:<10} {row[1] or 'N/A':<30} {row[2] or 'N/A':<12} {row[3] or 'N/A':<40}")
        print()



def view_all_events(conn,cur):
    print("\nAll Events:")
    cur.execute("SELECT eventID,eventName,eventType,eventDate,audienceType,eventLocation,roomNumber FROM Event ORDER BY eventDate DESC")
    rows=cur.fetchall()

    if not rows:
        print("No events found.")
        return
    
    print(f"{'Event ID':<8} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10} {'Location':<20} {'Room':<8}")
    print("-"*110)
    for row in rows:
        print(f"{row[0]:<8} {row[1] or 'N/A':<25} {row[2] or 'N/A':<15} {row[3] or 'N/A':<12} {row[4] or 'N/A':<10} {row[5] or 'N/A':<20} {row[6] or 'N/A':<8}")
        print()


def add_volunteering_position(conn,cur):
    while True:

        print("\nAdd volunteering position")

        position_name=input("Enter the position name (or type EXIT() to cancel): ").strip()
        if position_name.upper()=="EXIT()":
            print("Operation cancelled.")
            return
        location=input("Enter the location: ").strip()
        description=input("Enter the position description: ").strip()

        if not position_name or not location or not description:
            print("All fields are required.")
            continue

        # position automaticaly available

        cur.execute("INSERT INTO VolunteeringPositions (positionName,positionDescription,location,isAvailable) VALUES (?,?,?,?)",(position_name,description,location,1))
        position_id=cur.lastrowid

        conn.commit()
        print("Volunteering position added successfully!")
        print(f"Position ID: {position_id}")
        break
    
    

def add_event(conn,cur):
    while True:
        print("\nAdd an event")
        event_name=input("Enter the event name (or type EXIT() to cancel): ").strip()
        if event_name.upper()=="EXIT()":
            print("Operation cancelled.")
            return
        event_type=input("Enter the event type: ").strip()
        audience_type=input("Enter the audience type: ").strip()
        event_date=input("Enter the event date (YYYY-MM-DD) ").strip()
        event_location=input("Enter the event location ").strip()
        room_number=input("Enter the room number: ").strip()
        if not event_name or not event_type or not audience_type or not event_date or not event_location:
            print("All fields are required other than room number.")
            continue

        try:
            event_date_obj=date.fromisoformat(event_date)
        except ValueError:
            print("Invalid date format use YYYY-MM-DD.")
            continue

        cur.execute("INSERT INTO Event (eventName,eventType,audienceType,eventDate,eventLocation,roomNumber) VALUES (?,?,?,?,?,?)",(event_name,event_type,audience_type,event_date_obj.isoformat(),event_location,room_number))
        event_id=cur.lastrowid
        conn.commit()

        print("Event added successfully!")
        print(f"Event ID: {event_id}")
        break






def personnel_menu(conn,cur,personnel_id):
    while True:
        print("\nLIBRARY PERSONNEL MENU")
        print("1. View all members")
        print("2. View all borrowed items")
        print("3. View all volunteers")
        print("4. View all help requests")
        print("5. View all events")
        print("6. Add a volunteering position")
        print("7. Add an event")
        print("8. Exit")
        choice=input("Choose an option: ").strip()
        if choice.upper()=="EXIT()":
            print("Exiting menu.")
            break
        if choice=='1':
            view_all_members(conn,cur)
        elif choice=='2':
            view_all_borrowed_items(conn,cur)
        elif choice=='3':
            view_all_volunteers(conn,cur)
        elif choice=='4':
            view_all_help_requests(conn,cur)
        elif choice=='5':
            view_all_events(conn,cur)
        elif choice=='6':
            add_volunteering_position(conn,cur)
        elif choice=='7':
            add_event(conn,cur)
        elif choice=='8':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")



def main_menu(conn,cur,member_id):
    while True:
        print("\nLIBRARY MENU")
        print("1. Find an item")
        print("2. Borrow an item")
        print("3. Return an item")
        print("4. Donate an item")
        print("5. Find an event")
        print("6. Register for an event")
        print("7. Volunteer for the library")
        print("8. Ask a librarian for help")
        print("9. Exit")
        choice=input("Choose an option: ").strip()
        if choice.upper()=="EXIT()":
            print("Exiting menu.")
            break
        if choice=='1':
            find_item(conn,cur)
        elif choice=='2':
            borrow_item(conn,cur,member_id)
        elif choice=='3':
            return_item(cur,conn,member_id)
        elif choice=='4':
            donate_item(conn,cur)
        elif choice=='5':
            find_event(conn,cur)
        elif choice=='6':
            register_for_event(conn,cur,member_id)
        elif choice=='7':
            volunteer(conn,cur,member_id)
        elif choice=='8':
            request_help(conn,cur,member_id)
        elif choice=='9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")



def sign_in(conn,cur):
    while True:
        print("\nSign In Menu:")
        print("1. Sign in as a member")
        print("2. Sign in as a personnel")
        print("3. Register as a new member")
        print("4. Exit")

        choice=input("Choose an option: ").strip()

        if choice.upper()=="EXIT()":
            print("Exiting sign in.")
            return None,None
        
        if choice=='1':
            member_id=input("Enter your member ID (or type EXIT() to cancel): ").strip()

            if member_id.upper()=="EXIT()":
                continue

            first_name=input("Enter your first name: ").strip()
            cur.execute("SELECT * FROM Member WHERE memberID=?",(member_id,))

            result=cur.fetchone()

            if result:
                if result[1].lower()!=first_name.lower():
                    print("First name does not match the ID you provided")
                    continue

                print(f"Welcome back, {first_name}!")
                return ('member',result[0])
            
            else:
                print("We can't find a member with that ID")
                continue

        elif choice=='2':
            personnel_id=input("Enter your personnel ID (or type EXIT() to cancel): ").strip()
            if personnel_id.upper()=="EXIT()":
                continue

            first_name=input("Enter your first name: ").strip()

            cur.execute("SELECT * FROM Personnel WHERE personnelID=?",(personnel_id,))
            result=cur.fetchone()
            if result:
                if result[1].lower()!=first_name.lower():
                    print("First name does not match the personnel ID you provided")
                    continue

                print(f"Welcome back, {first_name}!")
                return ('personnel',result[0])
            else:
                print("Personnel ID not found.")
                continue

        elif choice=='3':
            member_id=register_member(conn,cur)
            if member_id is not None:
                print(f"Member ID: {member_id}")
                return ('member',member_id)
            
        elif choice=='4':
            print("Exiting...")
            return None,None
        
        else:
            print("Invalid choice. Try again.")



def register_member(conn,cur):
    # allows the user to register as a new member

    # returns the member ID of the newly registered member
    while True:
        print("\nRegister as a new member:")

        first_name=input("Enter your first name (or type EXIT() to cancel): ").strip()

        if first_name.upper()=="EXIT()":
            print("Registration cancelled.")
            return None
        
        last_name=input("Enter your last name: ").strip()
        email=input("Enter your email address: ").strip() or None
        phone_number=input("Enter your phone number: ").strip() or None
        
        if not first_name or not last_name:
            print("First name and last name are required.")
            continue

        if not phone_number and not email:
            print("Please provide at least one contact method (email or phone number).")
            continue

        cur.execute("INSERT INTO Member (firstName,lastName,email,phoneNumber) VALUES (?,?,?,?)",(first_name,last_name,email,phone_number))
        member_id=cur.lastrowid
        conn.commit()

        print("Registration successful!")
        print(f"Welcome, {first_name}! Your member ID is {member_id}.")
        print("Make sure to write it down for future reference, as you will need it to sign in")

        return member_id




def startup():
    conn,cur=connect_db()

    user_type,user_id=sign_in(conn,cur)
    if user_type is None:
        print("Exiting...")
        return
    
    if user_id is None:
        print("Unable to sign in. Exiting...")
        return
    
    print(f"Member Type: {user_type}")
    print(f"Member ID: {user_id}")

    # check if user is a member or personnel
    if user_type not in ['member','personnel']:
        print("Invalid user type, Exiting...") # should never happen
        return
    if user_type=='member':
        main_menu(conn,cur,user_id)
    elif user_type=='personnel':
        personnel_menu(conn,cur,user_id)



if __name__=='__main__':
    startup()
