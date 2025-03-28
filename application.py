import sqlite3
from datetime import date, timedelta
import time

def connect_db():
    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    return conn,cur

def find_item(conn,cur):
    while True:
        time.sleep(1)
        print("\nFind an item in the library:")
        print("Write 'EXIT()' to exit the search")
        keywords=input("Enter keywords to search for an item: ")
        if keywords=='EXIT()':
            break
        cur.execute("SELECT itemID,title,author,itemType,itemStatus FROM LibraryItem WHERE title LIKE ? OR author LIKE ? OR itemType LIKE ?", (f'%{keywords}%',f'%{keywords}%',f'%{keywords}%'))
        results=cur.fetchall()
        if results:
            print("Items found:")
            for row in results:
                print(f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}, Type: {row[3]}, Status: {row[4]}\n")
        else:
            print("No items found.")

def show_available_items(cur, limit=5):
    cur.execute("""
        SELECT itemID, title, author 
        FROM LibraryItem
        WHERE itemStatus = 'Available'
        ORDER BY itemID
        LIMIT ?
    """,(limit,))
    rows=cur.fetchall()
    if rows:
        print(f"\nHere are the first {len(rows)} available items (up to {limit}):")
        for r in rows:
            item_id,title,author=r
            print(f" - ID: {item_id} | Title: {title} | Author: {author}")
    else:
        print("\nNo items available at the moment.")




def borrow_item(conn,cur,member_id):
    while True:
        time.sleep(1)
        print("\nBorrow an item from the library:")
        print("Write 'EXIT()' to exit this operation")

        show_available_items(cur,limit=5)

        item_input=input("Enter the ID of the item you want to borrow: ").strip()
        if item_input.upper()=='EXIT()':
            print("Returning to main menu...")
            break

        if not item_input.isdigit():
            print("Invalid input. Please enter a numeric item ID.")
            continue

        item_id=int(item_input)
        cur.execute("SELECT itemStatus FROM LibraryItem WHERE itemID = ?", (item_id,))
        row=cur.fetchone()

        if not row:
            print("No item found with that ID.")
            continue

        status=row[0]
        if status!='Available':
            print(f"Item {item_id} is not available (status: {status}).")
            continue

        today=date.today()
        due=today+timedelta(days=14)

        try:
            cur.execute("INSERT INTO Borrows (itemID, memberID, borrowDate, dueDate) VALUES (?, ?, ?, ?)",(item_id,member_id,today.isoformat(),due.isoformat()))
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


def return_item(cur, conn, member_id):
    print("\n📦 Your borrowed (unreturned) items:")
    cur.execute("""
        SELECT B.itemID, L.title, L.author, B.borrowDate, B.dueDate
        FROM Borrows B
        JOIN LibraryItem L ON B.itemID = L.itemID
        WHERE B.memberID = ? AND B.returnDate IS NULL
    """, (member_id,))
    items = cur.fetchall()

    if not items:
        print("📭 You have no items to return.")
        return

    for item in items:
        print(f"🆔 {item[0]} | 📖 {item[1]} by {item[2]} | 📅 Borrowed: {item[3]} | Due: {item[4]}")

    while True:
        time.sleep(1)
        print("\nType the ID of the item to return (or type EXIT() to cancel):")
        item_input = input("Item ID: ").strip()
        
        if item_input.upper() == 'EXIT()':
            print("🔙 Return process cancelled.")
            break

        if not item_input.isdigit():
            print("❌ Invalid input. Please enter a valid item ID.")
            continue

        item_id = int(item_input)
        return_date = date.today().isoformat()

        try:
            cur.execute("""
                UPDATE Borrows 
                SET returnDate = ? 
                WHERE itemID = ? AND memberID = ? AND returnDate IS NULL
            """, (return_date, item_id, member_id))
            
            if cur.rowcount == 0:
                print("⚠️ That item is not currently borrowed by you or already returned.")
            else:
                conn.commit()
                print(f"Item {item_id} returned on {return_date}. Fine calculated if overdue.")
            break

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            break




def donate_item(conn,cur):
    title=input("Enter the title of the item you want to donate: ")
    author=input("Enter the author of the item: ")
    item_type=input("Enter the type of the item (e.g., Book, DVD, etc.): ")
    year=int(input("Enter the year of publication: "))
    #location=input("Enter where you want to donate the item (e.g., Main Library, Branch Library): ")
    issue=input("Enter the issue number (if applicable): ").strip() or None
    if issue is not None:
        issue_number=int(issue)

    cur.execute("INSERT INTO LibraryItem (title, author, itemType, releaseYear,issueNumber) VALUES (?, ?, ?, ?, ?)",(title,author, item_type, year, issue_number))
    item_id=cur.lastrowid
    conn.commit()
    print(f"Item donated successfully!")
    print(f"Item ID: {item_id}")
    print("Thank you for your donation!")




def find_event(conn,cur):
    keywords=input("Enter keywords to search for an event: ").strip()
    cur.execute("SELECT eventID,eventName,eventType,eventDate,audienceType FROM Event WHERE eventName LIKE ? OR eventType LIKE ? OR audienceType LIKE ?", (f'%{keywords}%',f'%{keywords}%',f'%{keywords}%'))
    results=cur.fetchall()
    if not results:
        print("No events found.")
        return
    
    print("Events Matching Your Search:")
    print(f"{'ID':<4}  {'Name':<25}  {'Type':<15}  {'Date':<12}  {'Audience':<10}")
    print("-"*70)

    # Print each row with neat spacing
    for (event_id,name,etype,edate,audience) in results:
        print(f"{event_id:<4}  {name:<25}  {etype:<15}  {edate:<12}  {audience:<10}")
    print()  # extra newline at en


def show_available_events(conn,cur,limit=5):
    cur.execute("""
        SELECT eventID, eventName, eventType, eventDate, audienceType 
        FROM Event
        ORDER BY eventID
        LIMIT ?
    """,(limit,))
    rows=cur.fetchall()
    if rows:
        print(f"\nHere are the first {len(rows)} available events (up to {limit}):")
        for r in rows:
            event_id,event_name,event_type,event_date,audience_type=r
            print(f" - ID: {event_id} | Name: {event_name} | Type: {event_type} | Date: {event_date} | Audience: {audience_type}")
    else:
        print("\nNo events available at the moment.")

def show_signed_up_events(conn,cur,member_id):
    cur.execute("""
        SELECT E.eventID, E.eventName, E.eventType, E.eventDate, E.audienceType 
        FROM Register R
        JOIN Event E ON R.eventID = E.eventID
        WHERE R.memberID = ?
    """, (member_id,))
    rows=cur.fetchall()
    if rows:
        print(f"\nHere are the events you are signed up for:")
        for r in rows:
            event_id,event_name,event_type,event_date,audience_type=r
            print(f" - ID: {event_id} | Name: {event_name} | Type: {event_type} | Date: {event_date} | Audience: {audience_type}")
    else:
        print("\nYou are not signed up for any events.")


def register_for_event(conn,cur,member_id):
    # maybe add event capacity
    print("\nRegister for an event:")
    show_signed_up_events(conn,cur,member_id)
    show_available_events(conn,cur)
    event_id=input("Enter the ID of the event you want to register for: ").strip()
    if not event_id.isdigit():
        print("Invalid input. Please enter a numeric event ID.")
        return
    
    try:
        event_id=int(event_id)
        cur.execute("INSERT INTO Register (memberID,eventID) VALUES (?,?)",(member_id,event_id))
        conn.commit()
        print("Registration successful!")
        print(f"You are now registered for event ID {event_id}.")
    except sqlite3.IntegrityError as e:
        print("You are already registered for this event.")
        print(f"DEBUG: {e}")
    except sqlite3.OperationalError as e:
        print(f"Operational Error: {e}")
        return
    





def sign_in(conn,cur):
    while True:
        print("\nAre you a member of the library?")
        print("1. Yes")
        print("2. No")
        choice=input("Choose an option: ")
        if choice=='2':
            print("Please register to become a member.")
            return register_member(conn,cur)
            break
        elif choice=='1':
            print("Please sign in.")
            member_id=input("Enter your member ID: ")
            first_name=input("Enter your first name: ")
            cur.execute("SELECT * FROM Member WHERE memberID=?", (member_id,))
            result=cur.fetchone()
            if result:
                if result[1] != first_name:
                    print("First name does not match. Please try again.")
                    continue
                print("Sign in successful!")
                print(f"Welcome back, {result[1]}!")
                return result[0]  # Return member ID
                break
            else:
                print("Member ID not found. Please try again.")
        else:
            print("Invalid choice. Try again.")



def register_member(conn,cur):
    while True:
        print("\nRegister as a new member:")
        first_name=input("Enter your first name: ")
        last_name=input("Enter your last name: ")
        email=input("Enter your email address: ").strip() or None
        phone_number=input("Enter your phone number: ").strip() or None
        #membershipType=input("Enter your membership type (e.g.,Student,Adult,Senior):").strip() or None
        if not first_name or not last_name:
            print("First name and last name are required.")
            continue
        if not phone_number and not email:
            print("Please provide at least one contact method (email or phone number).")
            return
        cur.execute("INSERT INTO Member (firstName,lastName,email,phoneNumber) VALUES (?,?,?,?)", (first_name,last_name,email,phone_number))
        member_id=cur.lastrowid
        conn.commit()
        print("Registration successful!")
        print(f"Welcome, {first_name}! your member ID is {member_id}.")
        print("Make sure to write it down for future reference.")
        return member_id  # Return member ID
        break



def main_menu():
    conn,cur=connect_db()
    member_id=sign_in(conn,cur)
    print(f"Member ID: {member_id}")
    if member_id is None:
        print("Unable to sign in. Exiting...")
        return
    while True:
        
        print("\n📚 LIBRARY MENU 📚")
        print("1. Find an item")
        print("2. Borrow an item")
        print("3. Return an item")
        print("4. Donate an item")
        print("5. Find an event")
        print("6. Register for an event")
        print("7. Volunteer for the library")
        print("8. Ask a librarian for help")
        print("9. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            find_item(conn,cur)
        elif choice == '2':
            borrow_item(conn,cur,member_id)
        elif choice == '3':
            return_item(cur,conn,member_id)
        elif choice == '4':
            donate_item(conn,cur)
        elif choice == '5':
            find_event(conn,cur)
        elif choice == '6':
            register_for_event(conn,cur,member_id)
        elif choice == '7': volunteer()
        elif choice == '8': request_help()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == '__main__':
    main_menu()