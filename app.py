## Emily Van Laarhoven and Naomi Day
## CS304 Assignment 6, Flask 2
## Due: 4/12/17 11:59pm

from flask import Flask, render_template, flash, request, redirect, url_for
import os
import hwk6 #other python file that interacts with db

app = Flask(__name__)
app.secret_key = "aeurhgaliursnfsd" #secret key needed for flashing

DATABASE = "evanlaar_db" #would change this line to wmdb

@app.route('/')
def home():
    return render_template("base.html",page_title="hwk6 home")

@app.route('/search/', methods=['POST','GET'])
def search():
    if request.method=="POST":
        cursor = hwk6.cursor()
        row = hwk6.search_partial_title(cursor,request.form['search-title'])
        if row:
            return redirect(url_for('update',tt=row['tt']))
        else:
            flash("Movie does not exist")
    return render_template("search.html",page_title="hwk6 home")

@app.route('/select/', methods=['POST','GET'])
def select():
    cursor = hwk6.cursor()
    if request.method=="POST":
        return redirect(url_for('update',tt=request.form['menu-tt'])) ###
    list_missing = hwk6.find_missing(cursor)
    return render_template("select.html",list_missing=list_missing)

@app.route('/update/<tt>', methods=['POST','GET'])
def update(tt):
    cursor = hwk6.cursor()
    if request.method=="POST":
        if request.form['submit']=='update':
            ## check if tt already in db
            new_tt = request.form['movie-tt']
            director = request.form['movie-director']
            ## check that director exists in person
            if (hwk6.check_director(cursor,director)):
                ## if new tt, check that new tt exists in person
                if (tt==new_tt): ##update movie if director, title, etc changed
                    hwk6.update_movie(cursor,request.form,tt)        
                    ## if tt has been updated and new_tt already exists in db flash error
                elif (tt != new_tt and not hwk6.check_tt(cursor,new_tt)):
                     flash("Movie already exists") ## do not update
                else:
                    ## update movie - there's a new tt
                    hwk6.update_movie(cursor,request.form,tt)
                    flash("Movie updated successfully")
                    return redirect(url_for("update",tt=new_tt))
            else:
                ## director does not exists in person table
                flash("Director does not exist")
        if request.form['submit']=='delete':
            # delete movie using tt
            if hwk6.delete_movie(cursor,tt):
                flash("Movie was deleted successfully")
                return redirect(url_for("home"))
    tt_list = hwk6.search_tt(cursor,tt) 
    if tt_list[4]==None:
        tt_list[4]="null"
    ## removed unnecessary redirects, XSS attack test 20 still failing
    return render_template("update.html",tt_list=tt_list)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
