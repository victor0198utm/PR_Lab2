package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"

	"server/models"

	filedriver "github.com/goftp/file-driver"
	"github.com/goftp/server"
	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

var FTP_up = false

func wellcome(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Endpoint Hit: home")
	fmt.Fprintf(w, "Welcome to the HTTP server!")
}

var sqliteDatabase *sql.DB

func exists(path string) bool {
	_, err := os.Stat(path)
	return !errors.Is(err, os.ErrNotExist)
}

func createDB() {
	path := "sqlite-database.db"
	fileExists := exists(path)
	if !fileExists {
		file, err := os.Create(path)

		if err != nil {
			log.Fatal(err.Error())
		}
		file.Close()
		log.Println("sqlite-database.db created")
	} else {
		fmt.Println("Database exists.")
	}

	var err error
	sqliteDatabase, err = sql.Open("sqlite3", path)
	if err != nil {
		log.Fatal(err)
	}
	// fmt.Println(sqliteDatabase)

	if !fileExists {
		createTable() // Create Database Tables
	}
}

func createTable() {
	createUserTableSQL := `CREATE TABLE user (
		"idUser" integer NOT NULL PRIMARY KEY AUTOINCREMENT,		
		"username" TEXT,
		"password" TEXT		
	  );`

	log.Println("Create user table...")
	statement, err := sqliteDatabase.Prepare(createUserTableSQL) // Prepare SQL Statement
	if err != nil {
		log.Fatal(err.Error())
	}
	statement.Exec() // Execute SQL Statements
	log.Println("user table created")

	createUserTableSQL = `CREATE TABLE file (
		"idFile" integer NOT NULL PRIMARY KEY AUTOINCREMENT,	
		"username" TEXT, 	
		"name" TEXT,
		"description" TEXT,
		"timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP	
	  );`

	log.Println("Create file table...")
	statement, err = sqliteDatabase.Prepare(createUserTableSQL) // Prepare SQL Statement
	if err != nil {
		log.Fatal(err.Error())
	}
	statement.Exec() // Execute SQL Statements
	log.Println("file table created")
}

func insertUser(user models.User) {
	log.Println("Inserting user record ...")
	insertStudentSQL := `INSERT INTO user(username, password) VALUES (?, ?)`
	// fmt.Println(sqliteDatabase)
	statement, err := sqliteDatabase.Prepare(insertStudentSQL) // Prepare statement. This is good to avoid SQL injections
	if err != nil {
		log.Fatalln(err.Error())
	}
	_, err = statement.Exec(user.Username, user.Password)
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func insertFile(newFile models.File) {
	log.Println("Inserting file record ...")
	insertStudentSQL := `INSERT INTO file(username, name, description) VALUES (?, ?, ?)`
	// fmt.Println(sqliteDatabase)
	statement, err := sqliteDatabase.Prepare(insertStudentSQL) // Prepare statement. This is good to avoid SQL injections
	if err != nil {
		log.Fatalln(err.Error())
	}
	_, err = statement.Exec(newFile.Username, newFile.Name, newFile.Description)
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func register(w http.ResponseWriter, r *http.Request) {
	var user models.User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Println("inserting user:", user.Username, user.Password)
	insertUser(user)

	if !FTP_up {
		FTP_up = true
		go ftp(user)
	}
}

func new(w http.ResponseWriter, r *http.Request) {
	var newFile models.File
	err := json.NewDecoder(r.Body).Decode(&newFile)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Println("inserting file:", newFile.Name, newFile.Description)
	insertFile(newFile)
}

func all(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusCreated)
	w.Header().Set("Content-Type", "application/json")

	path := "sqlite-database.db"
	fileExists := exists(path)
	if fileExists {
		sqliteDatabase, err := sql.Open("sqlite3", path)
		if err != nil {
			log.Fatal(err)
		}
		// fmt.Println(sqliteDatabase)

		fmt.Println("Getting files uploaded by:", sessionUsername)
		rows, err := sqliteDatabase.Query("SELECT * FROM file WHERE file.username LIKE '" + sessionUsername + "'")
		if err != nil {
			return
		}
		defer rows.Close()

		files := []models.FileRecord{}
		for rows.Next() {
			file := models.FileRecord{}
			if err := rows.Scan(&file.Id, &file.Username, &file.Name, &file.Description, &file.Uploaded); err != nil {
				return
			}
			files = append(files, file)
		}
		jsonResp, err := json.Marshal(files)
		if err != nil {
			log.Fatalf("Error happened in JSON marshal. Err: %s", err)
		}

		fmt.Println("Files:", files)

		w.Write(jsonResp)
	}
}

func handleRequests() {
	myRouter := mux.NewRouter().StrictSlash(true)
	myRouter.HandleFunc("/", wellcome).Methods("GET")
	myRouter.HandleFunc("/register", register).Methods("POST")
	myRouter.HandleFunc("/new", new).Methods("POST")
	myRouter.HandleFunc("/all", all).Methods("GET")
	log.Fatal(http.ListenAndServe(":8081", myRouter))
}

// fpt

func getUser(userDetails models.User) (string, string) {
	path := "sqlite-database.db"
	fileExists := exists(path)
	if fileExists {
		sqliteDatabase, err := sql.Open("sqlite3", path)
		if err != nil {
			log.Fatal(err)
		}
		// fmt.Println(sqliteDatabase)

		// fmt.Println("Getting user")
		querryStr := "SELECT * FROM user WHERE username LIKE '" + userDetails.Username + "'"
		// fmt.Println(querryStr)
		row, err := sqliteDatabase.Query(querryStr)
		if err != nil {
			log.Fatal(err)
		}
		defer row.Close()
		row.Next()
		// fmt.Println("Got one")
		var id int
		var username, password string
		row.Scan(&id, &username, &password)
		log.Println("User: ", username, " ", password)

		return username, password
	}

	return "", ""
}

var sessionUsername = ""

func ftp(userDetails models.User) {
	username, password := getUser(userDetails)
	if username == "" && password == "" {
		fmt.Println("No user registered")
		return
	}

	os.Mkdir(username, 0755)

	user := flag.String("user", username, "Username for login")
	pass := flag.String("pass", password, "Password for login")
	port := flag.Int("port", 2121, "Port")
	host := flag.String("host", "localhost", "Host")

	flag.Parse()
	if username == "" {
		log.Fatalf("Please set a root to serve with -root")
	}

	factory := &filedriver.FileDriverFactory{
		RootPath: username,
		Perm:     server.NewSimplePerm("user", "group"),
	}

	opts := &server.ServerOpts{
		Factory:  factory,
		Port:     *port,
		Hostname: *host,
		Auth:     &server.SimpleAuth{Name: *user, Password: *pass},
	}

	log.Printf("Starting ftp server on %v:%v", opts.Hostname, opts.Port)
	log.Printf("Username %v, Password %v", *user, *pass)
	serverI := server.NewServer(opts)
	sessionUsername = username
	err := serverI.ListenAndServe()
	if err != nil {
		log.Fatal("Error starting server:", err)
	}

}

func main() {

	createDB()

	handleRequests()

}
