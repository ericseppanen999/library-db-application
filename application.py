import sqlite3
from datetime import date,timedelta
import time



def connect_db():
    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    return conn,cur



def find_item(conn,cur):
    while True:
        time.sleep(1)
        print("\nFind an item in the library:")
        print("Type EXIT() to exit the search")
        keywords=input("Enter keywords: ").strip()
        if keywords.upper()=="EXIT()":
            break

        cur.execute("SELECT itemID,title,author,itemType,itemStatus FROM LibraryItem WHERE title LIKE ? OR author LIKE ? OR itemType LIKE ?",(f'%{keywords}%',f'%{keywords}%',f'%{keywords}%'))
        results=cur.fetchall()
        if results:

            print("Items found:")
            print(f"{'ID':<4} {'Title':<30} {'Author':<20} {'Type':<15} {'Status':<12}")
            print("-"*80)
            for row in results:
                print(f"{row[0]:<4} {row[1]:<30} {row[2]:<20} {row[3]:<15} {row[4]:<12}")
        else:
            print("No items found.")



def show_available_items(cur,limit=5):
    cur.execute("SELECT itemID,title,author FROM LibraryItem WHERE itemStatus='Available' ORDER BY itemID LIMIT ?",(limit,))
    rows=cur.fetchall()

    if rows:
        print(f"\nAvailable Items (up to {limit}):")
        print(f"{'ID':<4} {'Title':<30} {'Author':<20}")
        print("-"*60)
        for r in rows:
            print(f"{r[0]:<4} {r[1]:<30} {r[2]:<20}")
    else:
        print("\nNo items available at the moment.")



def borrow_item(conn,cur,member_id):
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
            print("Invalid input. Enter a numeric item ID.")
            continue

        item_id=int(item_input)
        cur.execute("SELECT itemStatus FROM LibraryItem WHERE itemID=?", (item_id,))
        row=cur.fetchone()

        if not row:
            print("No item found with that ID.")
            continue

        if row[0]!="Available":
            print(f"Item {item_id} is not available (Status: {row[0]}).")
            continue

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
            print("This item is already borrowed by you or another member.")
            print(f"DEBUG: {e}")
            continue

        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
            continue



def return_item(cur,conn,member_id):
    print("\nYour borrowed (unreturned) items:")
    cur.execute("SELECT B.itemID,L.title,L.author,B.borrowDate,B.dueDate FROM Borrows B JOIN LibraryItem L ON B.itemID=L.itemID WHERE B.memberID=? AND B.returnDate IS NULL",(member_id,))
    items=cur.fetchall()

    if not items:
        print("You have no items to return.")
        return
    
    print(f"{'ID':<4} {'Title':<30} {'Author':<20} {'Borrowed':<12} {'Due':<12}")
    print("-"*80)

    for item in items:
        print(f"{item[0]:<4} {item[1]:<30} {item[2]:<20} {item[3]:<12} {item[4]:<12}")
    while True:
        time.sleep(1)
        print("\nEnter the ID of the item to return (or type EXIT() to cancel):")
        item_input=input("Item ID: ").strip()
        if item_input.upper()=="EXIT()":
            print("Return process cancelled.")
            break

        if not item_input.isdigit():
            print("Invalid input. Enter a valid numeric item ID.")
            continue

        item_id=int(item_input)
        return_date=date.today().isoformat()
        try:
            cur.execute("UPDATE Borrows SET returnDate=? WHERE itemID=? AND memberID=? AND returnDate IS NULL",(return_date,item_id,member_id))
            if cur.rowcount==0:
                print("That item is not borrowed by you or already returned.")
            else:
                conn.commit()
                print(f"Item {item_id} returned on {return_date}.")
            break

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            break




def donate_item(conn,cur):
    print("\nDonate an item to the library:")
    title=input("Enter the title (or type EXIT() to cancel): ").strip()
    if title.upper()=="EXIT()":
        print("Donation cancelled.")
        return
    
    author=input("Enter the author (or type EXIT() to cancel): ").strip()
    if author.upper()=="EXIT()":
        print("Donation cancelled.")
        return
    
    item_type=input("Enter the type (e.g., Book, DVD) (or type EXIT() to cancel): ").strip()
    if item_type.upper()=="EXIT()":
        print("Donation cancelled.")
        return
    
    year_input=input("Enter the year of publication (or type EXIT() to cancel): ").strip()
    if year_input.upper()=="EXIT()":
        print("Donation cancelled.")
        return
    
    try:
        year=int(year_input)

    except:
        print("Invalid year input.")
        return
    
    issue=input("Enter the issue number if applicable (or type EXIT() to cancel): ").strip()
    if issue.upper()=="EXIT()":
        print("Donation cancelled.")
        return
    
    issue_number=None
    if issue:
        try:
            issue_number=int(issue)
        except:
            print("Invalid issue number.")
            return
        
    cur.execute("INSERT INTO LibraryItem (title,author,itemType,releaseYear,issueNumber) VALUES (?,?,?,?,?)",(title,author,item_type,year,issue_number))
    item_id=cur.lastrowid
    conn.commit()

    print("Item donated successfully!")
    print(f"Item ID: {item_id}")

    print("Thank you for your donation!")



def find_event(conn,cur):
    keywords=input("Enter keywords to search for an event (or type EXIT() to cancel): ").strip()
    if keywords.upper()=="EXIT()":
        print("Search cancelled.")
        return
    
    cur.execute("SELECT eventID,eventName,eventType,eventDate,audienceType FROM Event WHERE eventName LIKE ? OR eventType LIKE ? OR audienceType LIKE ?",(f'%{keywords}%',f'%{keywords}%',f'%{keywords}%'))
    results=cur.fetchall()
    if not results:
        print("No events found.")
        return
    
    print("Events Matching Your Search:")
    print(f"{'ID':<4} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10}")
    print("-"*70)

    for (event_id,name,etype,edate,audience) in results:
        print(f"{event_id:<4} {name:<25} {etype:<15} {edate:<12} {audience:<10}")
    print()



def show_available_events(conn,cur,limit=5):
    cur.execute("SELECT eventID,eventName,eventType,eventDate,audienceType FROM Event ORDER BY eventID LIMIT ?",(limit,))
    rows=cur.fetchall()
    if rows:
        print(f"\nAvailable Events (up to {limit}):")
        print(f"{'ID':<4} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10}")
        print("-"*70)
        for r in rows:
            print(f"{r[0]:<4} {r[1]:<25} {r[2]:<15} {r[3]:<12} {r[4]:<10}")
    else:
        print("\nNo events available at the moment.")



def show_signed_up_events(conn,cur,member_id):
    cur.execute("SELECT E.eventID,E.eventName,E.eventType,E.eventDate,E.audienceType FROM Register R JOIN Event E ON R.eventID=E.eventID WHERE R.memberID=?",(member_id,))
    rows=cur.fetchall()
    if rows:
        print("\nEvents You Are Registered For:")
        print(f"{'ID':<4} {'Name':<25} {'Type':<15} {'Date':<12} {'Audience':<10}")
        print("-"*70)

        for r in rows:
            print(f"{r[0]:<4} {r[1]:<25} {r[2]:<15} {r[3]:<12} {r[4]:<10}")
    else:
        print("\nYou are not registered for any events.")



def register_for_event(conn,cur,member_id):
    print("\nRegister for an event:")
    show_signed_up_events(conn,cur,member_id)
    show_available_events(conn,cur)
    event_id=input("Enter the ID of the event to register for (or type EXIT() to cancel): ").strip()
    if event_id.upper()=="EXIT()":
        print("Registration cancelled.")
        return
    
    if not event_id.isdigit():
        print("Invalid input. Enter a numeric event ID.")
        return
    
    try:
        event_id=int(event_id)
        cur.execute("INSERT INTO Register (memberID,eventID) VALUES (?,?)",(member_id,event_id))
        conn.commit()
        print("Registration successful!")
        print(f"Registered for event ID {event_id}.")

    except sqlite3.IntegrityError as e:
        print("You are already registered for this event.")
        print(f"DEBUG: {e}")

    except sqlite3.OperationalError as e:
        print(f"Operational Error: {e}")
        return



def print_available_jobs(conn,cur):
    cur.execute("SELECT positionID,positionName,positionDescription,location,isAvailable FROM VolunteeringPositions WHERE isAvailable=1 ORDER BY positionID")
    rows=cur.fetchall()

    if not rows:
        print("No available volunteering positions at the moment.")
        return
    print("Available Volunteering Positions:")

    print(f"{'ID':<4} {'Position Name':<25} {'Location':<20}")

    print("-"*60)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<25} {row[3]:<20}")
        if row[2]:
            print(f"Description: {row[2]}")
        print()



def print_current_volunteering_positions(conn,cur,member_id):
    cur.execute("SELECT V.positionID,P.positionName,P.positionDescription,P.location FROM Volunteer V JOIN VolunteeringPositions P ON V.positionID=P.positionID WHERE V.memberID=?",(member_id,))
    rows=cur.fetchall()

    if not rows:
        print("You are not registered for any volunteering positions.")
        return
    
    print("Your Volunteering Positions:")
    print(f"{'ID':<4} {'Position Name':<25} {'Location':<20}")
    print("-"*60)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<25} {row[3]:<20}")
        if row[2]:
            print(f"Description: {row[2]}")
        print()



def volunteer(conn,cur,member_id):
    print("\nVolunteer for the library:")
    print_current_volunteering_positions(conn,cur,member_id)
    print_available_jobs(conn,cur)

    positionid=input("Enter the ID of the position to volunteer for (or type EXIT() to cancel): ").strip()
    if positionid.upper()=="EXIT()":
        print("Volunteer process cancelled.")
        return
    
    if not positionid.isdigit():
        print("Invalid input. Enter a numeric position ID.")
        return
    
    positionid=int(positionid)
    cur.execute("SELECT isAvailable FROM VolunteeringPositions WHERE positionID=?",(positionid,))
    row=cur.fetchone()

    if not row:
        print("No position found with that ID.")
        return
    
    if row[0]==0:
        print(f"Position {positionid} is not available.")
        return
    
    try:
        cur.execute("INSERT INTO Volunteer (memberID,positionID) VALUES (?,?)",(member_id,positionid))
        cur.execute("UPDATE VolunteeringPositions SET isAvailable=0 WHERE positionID=?",(positionid,))
        conn.commit()
        print("Volunteer registration successful!")
        print(f"Registered for position ID {positionid}.")

    except sqlite3.IntegrityError as e:
        print("You are already registered for this position.")
        print(f"DEBUG: {e}")

    except sqlite3.OperationalError as e:
        print(f"Operational Error: {e}")
        return



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
            print("Unable to submit help request.")
            print(f"DEBUG: {e}")

        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
            return



def view_all_members(conn,cur):
    print("\nAll Members:")
    cur.execute("SELECT memberID,firstName,lastName,email,phoneNumber,membershipType FROM Member")

    rows=cur.fetchall()
    if not rows:
        print("No members found.")
        return
    
    print(f"{'ID':<4} {'Name':<30} {'Email':<25} {'Phone':<15}")
    print("-"*80)
    for row in rows:
        print(f"{row[0]:<4} {row[1]+' '+row[2]:<30} {row[3] or 'N/A':<25} {row[4] or 'N/A':<15}")
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
        print(f"{row[0]:<8} {row[1]:<30} {row[2]:<25} {row[3]:<12} {row[4]:<12}")
        print()



def view_all_volunteers(conn,cur):
    print("\nCurrently Registered Volunteers:")
    cur.execute("SELECT V.memberID,M.firstName||' '||M.lastName,P.positionName,P.location FROM Volunteer V JOIN Member M ON V.memberID=M.memberID JOIN VolunteeringPositions P ON V.positionID=P.positionID")
    rows=cur.fetchall()

    if not rows:
        print("No volunteers found.")
        return
    
    print(f"{'Member ID':<10} {'Name':<30} {'Position':<25} {'Location':<20}")
    print("-"*90)
    for row in rows:
        print(f"{row[0]:<10} {row[1]:<30} {row[2]:<25} {row[3]:<20}")
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
        print(f"{row[0]:<10} {row[1]:<30} {row[2]:<12} {row[3]:<40}")
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
        print(f"{row[0]:<8} {row[1]:<25} {row[2]:<15} {row[3]:<12} {row[4]:<10} {row[5]:<20} {row[6]:<8}")
        print()



def personnel_menu(conn,cur,personnel_id):
    while True:
        print("\nLIBRARY PERSONNEL MENU")
        print("1. View all members")
        print("2. View all borrowed items")
        print("3. View all volunteers")
        print("4. View all help requests")
        print("5. View all events")
        print("6. Exit")
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

            first_name=input("Enter your first name (or type EXIT() to cancel): ").strip()

            if first_name.upper()=="EXIT()":
                continue

            cur.execute("SELECT * FROM Member WHERE memberID=?",(member_id,))

            result=cur.fetchone()

            if result:
                if result[1].lower()!=first_name.lower():
                    print("First name does not match the member ID.")
                    continue

                print(f"Welcome back, {first_name}!")
                return ('member',result[0])
            
            else:
                print("Member ID not found.")
                continue

        elif choice=='2':
            personnel_id=input("Enter your personnel ID (or type EXIT() to cancel): ").strip()
            if personnel_id.upper()=="EXIT()":
                continue

            first_name=input("Enter your first name (or type EXIT() to cancel): ").strip()
            if first_name.upper()=="EXIT()":
                continue

            cur.execute("SELECT * FROM Personnel WHERE personnelID=?",(personnel_id,))
            result=cur.fetchone()
            if result:
                if result[1].lower()!=first_name.lower():
                    print("First name does not match the personnel ID.")
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
    while True:
        print("\nRegister as a new member:")

        first_name=input("Enter your first name (or type EXIT() to cancel): ").strip()

        if first_name.upper()=="EXIT()":
            print("Registration cancelled.")
            return None
        
        last_name=input("Enter your last name (or type EXIT() to cancel): ").strip()

        if last_name.upper()=="EXIT()":
            print("Registration cancelled.")
            return None
        
        email=input("Enter your email address (or type EXIT() to cancel): ").strip() or None

        if email and email.upper()=="EXIT()":
            print("Registration cancelled.")
            return None
        
        phone_number=input("Enter your phone number (or type EXIT() to cancel): ").strip() or None

        if phone_number and phone_number.upper()=="EXIT()":
            print("Registration cancelled.")
            return None
        
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
        print("Make sure to write it down for future reference.")

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

    if user_type=='member':
        main_menu(conn,cur,user_id)
    elif user_type=='personnel':
        personnel_menu(conn,cur,user_id)



if __name__=='__main__':
    startup()
