import streamlit as st
import sqlite3
import os

# Streamlit Config
st.set_page_config(page_title="Personal Library Manager", page_icon="📚", layout="wide")

# Database Configuration
DB_FILE = "library.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📂 Database Class
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row  # To fetch results as dictionaries
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publication_year INTEGER NOT NULL,
            genre TEXT,
            category TEXT CHECK(category IN ('Fiction', 'Non-Fiction')),
            read_status BOOLEAN NOT NULL DEFAULT 0,
            pic TEXT,
            rating INTEGER DEFAULT 0
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

# Sidebar Menu
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio("Navigation", ["➕ Add Book", "🖊 Update Book", "🗑 Remove Book", "🔍 Search Books", "📖 View All Books", "📊 Statistics"])

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
        uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg"], label_visibility="visible")

        if uploaded_file:
            st.image(uploaded_file, caption="Book Cover Preview", width=200)

        submit = st.form_submit_button("➕ Add Book")

        if submit and title and author:
            pic_path = None
            if uploaded_file:
                pic_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(pic_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            db.execute_query(
                "INSERT INTO books (title, author, publication_year, genre, category, read_status, rating, pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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
            st.markdown('<p class="section-header">📚 Update Book Information</p>', unsafe_allow_html=True)

            title = st.text_input("📖 Title", book["title"])
            author = st.text_input("✍️ Author", book["author"])
            year = st.number_input("📅 Publication Year", min_value=1000, max_value=2025, step=1, value=book["publication_year"])
            genre = st.text_input("📂 Genre", book["genre"])
            category = st.radio("📌 Category", ["Fiction", "Non-Fiction"], index=0 if book["category"] == "Fiction" else 1)
            rating = st.slider("⭐ Rating", 0, 5, book["rating"])

            read_status_value = 1 if st.checkbox("✅ Mark as Read", value=book["read_status"]) else 0

            st.markdown('<p class="section-header">📸 Current Book Cover</p>', unsafe_allow_html=True)
            if book["pic"]:
                st.image(book["pic"], caption="Current Book Cover", width=200)

            st.markdown('<p class="section-header">📸 Upload New Book Cover (Optional)</p>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"], label_visibility="visible")

            submit = st.form_submit_button("🖊 Update Book")

            if submit:
                pic_path = book["pic"]
                if uploaded_file:
                    pic_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                    with open(pic_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                db.execute_query(
                    "UPDATE books SET title=?, author=?, publication_year=?, genre=?, category=?, read_status=?, rating=?, pic=? WHERE id=?",
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
            db.execute_query("DELETE FROM books WHERE id=?", (book["id"],))
            st.success(f"🗑 Book '{book['title']}' removed successfully!")
    else:
        st.info("⚠ No books available to remove.")


#  **Search Books**
elif menu == "🔍 Search Books":
    st.markdown('<p class="title">Search for Books</p>', unsafe_allow_html=True)
    search_term = st.text_input("🔎 Enter book title or author:", key="search_input")

    if st.button("🔍 Search", key="search_button"):
        if search_term:
            results = db.execute_query("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
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
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    if book["pic"]:
                        st.image(book["pic"], caption="Book Cover", width=100)
                    else:
                        st.image("https://via.placeholder.com/100x150?text=No+Cover", caption="No Cover", width=100)

                with col2:
                    st.markdown(f"### 📖 {book['title']}")
                    st.markdown(f"**Author:** ✍️ {book['author']}")
                    st.markdown(f"**Year:** 📅 {book['publication_year']}")
                    st.markdown(f"**Genre:** 📂 {book['genre']}")
                    st.markdown(f"**Category:** 📌 {book['category']}")
                    read_status_label = "✔ Read" if int(book["read_status"]) == 1 else "❌ Unread"
                    st.markdown(f"**Status:** {read_status_label}")
                    st.markdown(f"**Rating:** ⭐ {book['rating']} / 5")

                st.markdown("---")
    else:
        st.info("📂 Your library is empty.")


# **Statistics**
elif menu == "📊 Statistics":
    st.markdown('<p class="title">Library Statistics</p>', unsafe_allow_html=True)

    read_books = db.execute_query("SELECT COUNT(*) AS count FROM books WHERE read_status = 1", fetch=True)[0]['count']
    unread_books = db.execute_query("SELECT COUNT(*) AS count FROM books WHERE read_status = 0", fetch=True)[0]['count']
    total_books = read_books + unread_books
    category_stats = db.execute_query("SELECT category, COUNT(*) AS count FROM books GROUP BY category", fetch=True)

    st.markdown(f"""
        <div class="stat-container">
            <div class="stat-card">
                <h5>📚 Total Books</h5>
                <p>{total_books}</p>
            </div>
            <div class="stat-card">
                <h5>📖 Read Books</h5>
                <p>{read_books}</p>
            </div>
            <div class="stat-card">
                <h5>📕 Unread Books</h5>
                <p>{unread_books}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="category-header">📊 Category-wise Distribution</p>', unsafe_allow_html=True)
    
    if category_stats:
        col1, col2 = st.columns(2)
        with col1:
            for category in category_stats[:len(category_stats)//2]:
                st.markdown(f"""
                    <div class="stat-card">
                        <h5>{category['category']}</h5>
                        <p>{category['count']} books</p>
                    </div>
                """, unsafe_allow_html=True)
        with col2:
            for category in category_stats[len(category_stats)//2:]:
                st.markdown(f"""
                    <div class="stat-card">
                        <h5>{category['category']}</h5>
                        <p>{category['count']} books</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("⚠ No category statistics available.")

db.close()
