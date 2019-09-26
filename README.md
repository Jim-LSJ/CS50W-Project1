# Project 1

### Web Programming with Python and JavaScript

### link: https://cs50w-project1-jim.herokuapp.com/

---
### Register

![](https://i.imgur.com/UpRwsLm.png)

- After registeration, I use script to redirect to the login page.
![](https://i.imgur.com/eKDEblf.png)

### Log in
![](https://i.imgur.com/MY6HgCi.png)

### Homepage
![](https://i.imgur.com/lZ9bhqe.png)

1. navbar
![](https://i.imgur.com/brYp5KV.png)
    - Search book through this search blank.
    - Hover on the user icon to show the username.
    - Return to home page by press the user icon.
    ![](https://i.imgur.com/wAL45zm.png)
    - Log out.
    
2. Direct to another pages
![](https://i.imgur.com/ePQYyyT.png)
    - Press `Home` to return Home page
    - Press `Search` to the Search page
    - Press `Top 10 reviews` to see the ten books with the most reviews.

3. Search books
![](https://i.imgur.com/DrI3khn.png)
    - Search books here or through the navbar.

4. Check the book information.
![](https://i.imgur.com/0kP9IaN.png)
    - Under the Search block, there are many bootstrap cards.
    - When hovered, there will be shadow surronding the cards.
    - Click the card to see the detail information of the books.
    
5. Select the pages
![](https://i.imgur.com/Gzeggsz.png)
![](https://i.imgur.com/iiHN9r3.png)
    - At home page, every page have only 9 cards ordered by their id in database.
    - At the bottom of the Home page, you can change to another pages to show the other 9 books.

### Search Page
![](https://i.imgur.com/gsBvNZM.png)
- Nothing but the navbar and the search block.

### Top 10 reviews
![](https://i.imgur.com/IyAFRda.png)
- There are 10 cards in this page, and reviews count also shows on each card.

### Search
- After searching, you will see the results showed like this.
![](https://i.imgur.com/alCE8ln.png)
- If the results of your key word are more than 30, it will only show 30 cards. (I have considered whether I need to show all the resuls like the home page style, but I think it's not necessary.)
![](https://i.imgur.com/RPHiYOM.png)

### Book
![](https://i.imgur.com/wbPxpxI.png)
- The link below the image is `"https://www.goodreads.com/search?q=" + str(book_info['isbn'])`
- The image url is what I use request.get(url) to get the html file and parse by bs4.
- User can leave a review and rate to the book.
- User reviews will be showed like this.
![](https://i.imgur.com/g9EaijU.png)
- If a user leave multiple reviews
![](https://i.imgur.com/l13lfKG.png)
- If a user doesn't type anything and submit
![](https://i.imgur.com/torI3XI.png)

### API Access
- Show the json
![](https://i.imgur.com/KWGUkHe.png)
- No isbn matching
![](https://i.imgur.com/LqBFjRK.png)

### Addition
- Favicon
![](https://i.imgur.com/qB4NMFY.png)
- Some animations like fade-in from right to left.

### Database
1. books
![](https://i.imgur.com/8S4Vbi3.png)
2. reviews
![](https://i.imgur.com/mt3iWdU.png)
3. users
![](https://i.imgur.com/h86Uiiu.png)
