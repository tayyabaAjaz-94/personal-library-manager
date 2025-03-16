import streamlit as st
import mysql.connector
import os

#  Streamlit Config
st.set_page_config(page_title="Personal Library Manager", page_icon="📚", layout="wide")

#  Database Configuration
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "library_db"
# }

db = mysql.connector.connect(
        user='root', 
        password='', 
        host='localhost', 
        database='library_db'
    )
 


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📂 Database Class
class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            publication_year INT NOT NULL,
            genre VARCHAR(100),
            category ENUM('Fiction', 'Non-Fiction'),
            read_status BOOLEAN NOT NULL DEFAULT 0,
            pic VARCHAR(255),
            rating INT DEFAULT 0
        )"""
        self.cursor.execute(query)
        self.conn.commit()

    def execute_query(self, query, values=None, fetch=False):
        self.cursor.execute(query, values or ())
        data = self.cursor.fetchall() if fetch else None
        self.conn.commit()
        return data

    def close(self):
        self.cursor.close()
        self.conn.close()

db = Database()

#  Sidebar Menu
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio("", ["➕ Add Book", "🖊 Update Book", "🗑 Remove Book", "🔍 Search Books", "📖 View All Books", "📊 Statistics"])

# UI Styling
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f8f8;
        }
        .title {
            font-size: 2.5em;
            color: #4B9CD3;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }
        .section-header {
            font-size: 1.8em;
            color: #333;
            margin-top: 20px;
            margin-bottom: 10px;
            text-align: left;
            font-weight: bold;
        }
        .form-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        .upload-box {
            border: 2px dashed #4B9CD3;
            border-radius: 8px;
            padding: 20px;
            background-color: #f0f8ff;
            text-align: center;
        }
        .upload-box input[type="file"] {
            display: none;
        }
        .upload-box label {
            background-color: #4B9CD3;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
        }
        .upload-box label:hover {
            background-color: #337AB7;
        }
        .upload-preview {
            margin-top: 15px;
            width: 150px;
            height: 200px;
            object-fit: cover;
            border-radius: 5px;
        }
        .btn {
            background-color: #4B9CD3;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            display: block;
            margin: 20px auto;
            font-size: 1.2em;
            width: 100%;
        }
        .btn:hover {
            background-color: #337AB7;
        }
    </style>
""", unsafe_allow_html=True)


#  **Add Book**
if menu == "➕ Add Book":
    st.markdown('<p class="title">Add a New Book</p>', unsafe_allow_html=True)
    with st.form("add_book_form", clear_on_submit=True):
        st.markdown('<p class="section-header">Book Information</p>', unsafe_allow_html=True)

        title = st.text_input("📖 Title", placeholder="Enter book title")
        author = st.text_input("✍️ Author", placeholder="Enter author's name")
        year = st.number_input("📅 Publication Year", min_value=1000, max_value=2025, step=1, placeholder="Enter year")
        genre = st.text_input("📂 Genre", placeholder="Enter book genre")
        category = st.radio("📌 Category", ["Fiction", "Non-Fiction"])

        read_status_value = 1 if st.checkbox("✅ Mark as Read") else 0
        rating = st.slider("⭐ Rating", 0, 5, 0)

        st.markdown('<p class="section-header">Upload Book Cover (Optional)</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            # Adjust the width and height of the book cover image for professional display
            st.image(uploaded_file, caption="Book Cover Preview", width=200)  # Adjust width to a more reasonable size

        submit = st.form_submit_button("➕ Add Book")

        if submit and title and author:
            pic_path = None
            if uploaded_file:
                pic_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(pic_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            db.execute_query(
                "INSERT INTO books (title, author, publication_year, genre, category, read_status, rating, pic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (title, author, year, genre, category, read_status_value, rating, pic_path)
            )
            st.success(f"✅ Book '{title}' added successfully!")


#  **Update Book**
elif menu == "🖊 Update Book":
    st.markdown('<p class="title">Update an Existing Book</p>', unsafe_allow_html=True)

    books = db.execute_query("SELECT * FROM books", fetch=True)

    if books:
        book_options = {book["title"]: book for book in books}
        selected_title = st.selectbox("📖 Select book to update", list(book_options.keys()))
        book = book_options[selected_title]

        with st.form("update_book_form"):
            # Heading for book info
            st.markdown('<p class="section-header">📚 Update Book Information</p>', unsafe_allow_html=True)

            # Book information input fields
            title = st.text_input("📖 Title", book["title"])
            author = st.text_input("✍️ Author", book["author"])
            year = st.number_input("📅 Publication Year", min_value=1000, max_value=2025, step=1, value=book["publication_year"])
            genre = st.text_input("📂 Genre", book["genre"])
            category = st.radio("📌 Category", ["Fiction", "Non-Fiction"], index=0 if book["category"] == "Fiction" else 1)
            rating = st.slider("⭐ Rating", 0, 5, book["rating"])

            # Read/Unread status checkbox
            read_status_value = 1 if st.checkbox("✅ Mark as Read", value=book["read_status"]) else 0

            # Show current book cover image if available
            st.markdown('<p class="section-header">📸 Current Book Cover</p>', unsafe_allow_html=True)
            if book["pic"]:
                st.image(book["pic"], caption="Current Book Cover", width=200)

            st.markdown('<p class="section-header">📸 Upload New Book Cover (Optional)</p>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

            submit = st.form_submit_button("🖊 Update Book")

            if submit:
                # Retain previous picture if no new file is uploaded
                pic_path = book["pic"]
                if uploaded_file:
                    pic_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                    with open(pic_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                # Update the book in the database
                db.execute_query(
                    "UPDATE books SET title=%s, author=%s, publication_year=%s, genre=%s, category=%s, read_status=%s, rating=%s, pic=%s WHERE id=%s",
                    (title, author, year, genre, category, read_status_value, rating, pic_path, book["id"])
                )
                st.success(f"✅ Book '{title}' updated successfully!")
    else:
        st.info("⚠ Please add at least one book to update.")



#  **Remove Book**
elif menu == "🗑 Remove Book":
    st.markdown('<p class="title">Remove a Book</p>', unsafe_allow_html=True)
    books = db.execute_query("SELECT * FROM books", fetch=True)

    if books:
        book_options = {book["title"]: book for book in books}
        selected_title = st.selectbox("📖 Select book to remove", list(book_options.keys()))
        book = book_options[selected_title]

        if st.button("🗑 Confirm Remove"):
            db.execute_query("DELETE FROM books WHERE id=%s", (book["id"],))
            st.success(f"🗑 Book '{book['title']}' removed successfully!")
    else:
        st.info("⚠ No books available to remove.")


#  **Search Books**
elif menu == "🔍 Search Books":
    st.markdown('<p class="title">Search for Books</p>', unsafe_allow_html=True)
    search_term = st.text_input("🔎 Enter book title or author:")

    # Add search button
    if st.button("🔍 Search"):
        if search_term:
            results = db.execute_query("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", 
                                       (f"%{search_term}%", f"%{search_term}%"), fetch=True)
            if results:
                for book in results:
                    read_status_label = "✔ Read" if book["read_status"] == 1 else "❌ Unread"
                    st.write(f"📖 {book['title']} by {book['author']} ({book['publication_year']}) - {read_status_label} - {book['category']}")
            else:
                st.info("🔍 No matching books found.")
        else:
            st.warning("⚠ Please enter a title or author to search.")

# **View All Books**
elif menu == "📖 View All Books":
    st.markdown('<p class="title">View All Books in Your Library</p>', unsafe_allow_html=True)
    books = db.execute_query("SELECT * FROM books", fetch=True)

    if books:
        for book in books:
            # Create a container for each book (vertical layout)
            with st.container():
                # Layout for book information in vertical way
                col1, col2 = st.columns([1, 3])  # Two columns: one for image, one for details

                with col1:
                    # Show the book cover image in a small size
                    if book["pic"]:
                        st.image(book["pic"], caption="Book Cover", width=100)  # Small image (adjust size)
                    else:
                        st.image("https://via.placeholder.com/100x150?text=No+Cover", caption="No Cover", width=100)

                with col2:
                    # Display book information in a clean, professional vertical layout
                    st.markdown(f"### 📖 {book['title']}")
                    st.markdown(f"**Author:** ✍️ {book['author']}")
                    st.markdown(f"**Year:** 📅 {book['publication_year']}")
                    st.markdown(f"**Genre:** 📂 {book['genre']}")
                    st.markdown(f"**Category:** 📌 {book['category']}")
                    read_status_label = "✔ Read" if int(book["read_status"]) == 1 else "❌ Unread"
                    st.markdown(f"**Status:** {read_status_label}")
                    st.markdown(f"**Rating:** ⭐ {book['rating']} / 5")

                st.markdown("---")  # Divider between books
    else:
        st.info("📂 Your library is empty.")


# 📊 **Statistics**
# 📊 **Statistics**
elif menu == "📊 Statistics":
    st.markdown('<p class="title">Library Statistics</p>', unsafe_allow_html=True)

    # Query statistics from the database
    read_books = db.execute_query("SELECT COUNT(*) AS count FROM books WHERE read_status = 1", fetch=True)[0]['count']
    unread_books = db.execute_query("SELECT COUNT(*) AS count FROM books WHERE read_status = 0", fetch=True)[0]['count']
    total_books = read_books + unread_books
    category_stats = db.execute_query(""" 
        SELECT category, COUNT(*) AS count FROM books GROUP BY category 
    """, fetch=True)

    # Display the stats in a grid layout
    st.markdown('<div class="stat-container">', unsafe_allow_html=True)
    st.markdown("""
        <style>
            .stat-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-top: 20px;
                padding: 20px;
                border-radius: 8px;
            }
            .stat-card {
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
                background-color: transparent;  /* No background color */
            }
            .stat-card h5 { /* Changed h4 to h5 */
                font-size: 1.4em;
                margin-bottom: 10px;
                color: #4A90E2; /* Lighter blue color for all h5 headings */
            }
            .stat-card p {
                font-size: 1.2em;
                color: white; /* White color for all p text */
            }
            .category-header {
                font-size: 1.8em;
                color: #4A90E2; /* Lighter blue color for the category distribution heading */
                font-weight: bold;
                margin-top: 30px;
                margin-bottom: 15px;
                text-align: center;
            }
            .title {
                font-size: 2em;
                color: #4A90E2; /* Lighter blue color for Library Statistics heading */
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }
            .section-header {
                font-size: 1.8em;
                color: #4A90E2; /* Lighter blue color for section headers */
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Display the total, read, and unread books in "cards"
    st.markdown(f"""
        <div class="stat-card">
            <h5>📚 Total Books</h5>  <!-- Changed h4 to h5 -->
            <p>{total_books}</p>
        </div>
        <div class="stat-card">
            <h5>📖 Read Books</h5>  <!-- Changed h4 to h5 -->
            <p>{read_books}</p>
        </div>
        <div class="stat-card">
            <h5>📕 Unread Books</h5>  <!-- Changed h4 to h5 -->
            <p>{unread_books}</p>
        </div>
    """, unsafe_allow_html=True)

    # Highlight the "Category-wise Distribution" heading in light blue
    st.markdown('<p class="category-header">📊 Category-wise Distribution</p>', unsafe_allow_html=True)
    
    if category_stats:
        # Display categories in cards within two columns
        col1, col2 = st.columns(2)
        with col1:
            for category in category_stats[:len(category_stats)//2]:
                st.markdown(f"""
                    <div class="stat-card">
                        <h5>{category['category']}</h5>  <!-- Changed h4 to h5 -->
                        <p>{category['count']} books</p>
                    </div>
                """, unsafe_allow_html=True)
        with col2:
            for category in category_stats[len(category_stats)//2:]:
                st.markdown(f"""
                    <div class="stat-card">
                        <h5>{category['category']}</h5>  <!-- Changed h4 to h5 -->
                        <p>{category['count']} books</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("⚠ No category statistics available.")


db.close()
