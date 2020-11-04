from datetime import date

class User():
    def __init__(self, c, conn, uid, name):
        print("\nWelcome",uid)
        self.c = c
        self.conn = conn
        self.uid = uid
        self.name = name
        self.pid = 'test1'
        self.isQuestion = False

    def menu(self):
        print('''Menu--------
        1-Logout
        2-Exit Program
        3-Post a question
        4-Search for posts''')
        option = input("Option: ")
        if option=="1":
            #logout
            print("\n Logged Out\n")
            # jump out to main function
            return None
        elif option=="2":
            self.conn.close()
            quit()
        elif option=="3":
            self.post()
        elif option=="4":
            self.search()
        else:
            print("\nNot a Valid Option\n")
            return self.menu()
    
    def postActionMenu(self):
        if self.isQuestion:
            # post answer is only an option is selected post is a question
            print('''Post Action--------
            1-Main Menu
            2-Vote on post
            3-Post an answer''')
        else:
            print('''Post Action--------
            1-Main Menu
            2-Vote on post''')
        print('Selected Post ID: ',self.pid)
        option = input("Option: ")
        if option=="1":
            self.menu()
        elif option=="2":
            self.vote()
        elif option=="3":
            if self.isQuestion:
                self.answer()
            else:
                print("\nNot a Valid Option\n")
                return self.menu()
        else:
            print("\nNot a Valid Option\n")
            return self.menu()

    def post(self):
        print("\n -----Post a Question-----")
        self.c.execute('SELECT COALESCE(MAX(pid),0) FROM posts;')
        pid = int(self.c.fetchone()[0])+1
        title = input("Enter Title: ")
        body = input("Enter Body: ")
        poster_id = self.uid

        self.c.execute('''INSERT INTO posts(pid,pdate,title,body,poster) 
        VALUES(:pid, :pdate, :title, :body, :poster);''',
        { 'pid':pid, 'pdate':date.today(), 'title':title, 'body':body, 'poster':poster_id })
        
        self.c.execute('''INSERT INTO questions(pid) 
        VALUES(:pid);''',
        { 'pid':pid })
        
        self.conn.commit()
        print("\nYour question has been posted\n")
        self.menu()

    def search(self):
        print("\n -----Search for posts-----")
        entry = input("Please enter a keyword: \n")
        entry.lower()
        keywords = entry.split(' ')
        keywords[:] = [item for item in keywords if item != '']

        find_matches = '''SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as SearchIndex, c.Type, p.pid, p.pdate, p.title, p.body, p.poster, COALESCE(A.Num_of_Answers,0) AS Num_of_Answers, COALESCE(B.Total_Votes,0) AS Total_Votes
                        FROM posts p
                        LEFT OUTER JOIN
                        (SELECT  'Answer' AS Type, a.pid
                        FROM answers a 
                        UNION
                        SELECT  'Question' AS Type, q.pid
                        FROM questions q) as C on C.pid = p.pid
                        LEFT OUTER JOIN
                        (SELECT  p1.pid, COALESCE(COUNT(a1.qid),0) AS Num_of_Answers
                        FROM posts p1, answers a1
                        WHERE p1.pid = a1.qid
                        GROUP BY (p1.pid)
                        ) as A on A.pid = p.pid
                        LEFT OUTER JOIN
                        (SELECT  p2.pid,COUNT(v2.pid) AS Total_Votes
                        FROM posts p2, votes v2
                        WHERE p2.pid = v2.pid
                        GROUP BY (p2.pid)
                        ) as B on B.pid = p.pid
                        LEFT OUTER JOIN
                        (SELECT p3.pid AS test
                        FROM posts p3, tags t
                        WHERE p3.pid = t.pid
                        AND lower(t.tag) like '%{}%') as C on C.test = p.pid
                        WHERE 
                        (lower(p.title) like '%{}%' or lower(p.body) like '%{}%' )
                        GROUP BY p.pid
                        ORDER BY COUNT(p.pid) DESC;
                    '''.format('%\' OR lower(t.tag) like \'%'.join(keywords), 
                               '%\' OR lower(p.title) like \'%'.join(keywords),
                               '%\' OR lower(p.body) like \'%'.join(keywords))
        ## NOT SURE HOW TO SEARCH MULTIPLE KEYWORDS
        self.c.execute(find_matches)

        rows = self.c.fetchall()

        output_array = []
        output_array = [list(i) for i in rows]

        if len(output_array) == 0:
            print('\nSorry! There are no matches found\n')
            self.menu()

        for i in range(len(output_array)):
            if i != 0 and i % 5 == 0:
                inp_1 = input("\nEither select a search index number or enter 'x' to see more posts\n")
                inp_1.lower()

                if (inp_1 == "x"):
                    print('\n', output_array[i], '\n')

                elif (inp_1.isdigit()):

                    selected_post_id = output_array[int(inp_1) - 1][2]
                    print("User has selected post #", selected_post_id, "\n")
                    self.pid = int(selected_post_id)

                    if output_array[int(inp_1) - 1][1] == "Question":
                        self.isQuestion = True
                    else:
                        self.isQuestion = False
                    self.postActionMenu()
            else:
                print('\n', output_array[i])

        inp_1 = input("Please select a post using the search index number\n")
        inp_1.lower()
        if (inp_1.isdigit() and int(inp_1) <= len(output_array)):
            selected_post_id = output_array[int(inp_1) - 1][2]
            print("User has selected post #", selected_post_id, "\n")
            self.pid = int(selected_post_id)

            if output_array[int(inp_1) - 1][1] == "Question":
                self.isQuestion = True
            else:
                self.isQuestion = False
            self.postActionMenu()
        else:
            print('\nInvalid Selection\n')
            self.menu()

    def answer(self):
        print("\n -----Post an Answer-----")
        qid = self.pid
        self.c.execute('SELECT COALESCE(MAX(pid),0) FROM posts;')
        aid = int(self.c.fetchone()[0])+1
        title = input("Enter Title: ")
        body = input("Enter Body: ")
        poster_id = self.uid

        self.c.execute('''INSERT INTO posts(pid,pdate,title,body,poster) 
        VALUES(:aid, :pdate, :title, :body, :poster);''',
        { 'aid':aid, 'pdate':date.today(), 'title':title, 'body':body, 'poster':poster_id })

        self.c.execute('''INSERT INTO answers(pid,qid) 
        VALUES(:aid, :qid);''',
        { 'aid':aid, 'qid':qid })
            
        self.conn.commit()
        print("\nYour answer has been recorded\n")
        self.menu()

    '''
        Post action-Vote.The user should be able to vote on the post (if not voted already on the same post). 
        The vote should be recorded in the database with a vno assigned by your system, the vote date set to the 
        current date and the user id is set to the current user.
    '''
    def vote(self):
        # check that user has not already voted on the post
        self.c.execute('SELECT * FROM votes WHERE pid=:pid AND uid=:uid',{'pid':self.pid, 'uid':self.uid})
        if (self.c.fetchone() == None):
            # has not voted
            # generate a unique vno
            self.c.execute('SELECT COALESCE(MAX(vno),0) FROM votes;')
            vno = int(self.c.fetchone()[0])+1
 
            # insert vote into database
            self.c.execute('INSERT INTO votes(pid,vno,vdate,uid) VALUES(:pid,:vno,:vdate,:uid);',
                {'pid':self.pid, 'vno':vno ,'vdate':date.today(), 'uid':self.uid})
            self.conn.commit()
            print('\nVoted on Post',self.pid,"\n")
            self.postActionMenu()
        else:
            print('\nAlready Voted on Post',self.pid,"\n")
            self.postActionMenu()
        

