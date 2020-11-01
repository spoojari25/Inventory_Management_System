
from flask import Flask, render_template,flash,redirect,url_for,request,session, Response
from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.secret_key = "pro"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models

class Product(db.Model):
    _id = db.Column( db.Integer, primary_key=True)
    pro_name = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return self.pro_name 


class Location(db.Model):
    _id = db.Column( db.Integer, primary_key=True)
    loc_name = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return self.loc_name 

class Movement(db.Model):
    _id = db.Column( db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(100))
    to_location = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    product_id = db.Column(db.Integer, nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return self._id


#Routing To Home Page

@app.route("/",methods = ["POST","GET"])
def home():
    return render_template("home.html")


@app.route("/product", methods = ["GET","POST"])
def product():

    if request.method=="POST":    
        if 'pro_id' in request.form:
            pro_id = request.form["pro_id"] 
            pro_present = Product.query.filter_by(_id=pro_id).first()
            pro_present.pro_name = request.form["edit_pro"]
            db.session.commit()
            flash(f" Product is Successfully Updated to '{ pro_present.pro_name }' ","success")
        if 'pro_name' in request.form:
            pro_name = request.form["pro_name"]
            pro_name = pro_name.capitalize()
            if Product.query.filter_by(pro_name=pro_name).first():
                flash(f"'{pro_name}' already exists in records!", "warning")
            else:
                new_product = Product(pro_name = pro_name)
                db.session.add(new_product)
                db.session.commit()
                flash(f"Product '{ new_product }' is Saved Succesfully!","success")     
    products = Product.query.all()
    return render_template('product.html',products = products)

@app.route("/location",methods=["GET","POST"])
def location():
    if request.method=="POST":
        if 'loc_id' in request.form:
            loc_id = request.form["loc_id"] 
            loc_present = Location.query.filter_by(_id=loc_id).first()
            loc_present.loc_name = request.form["edit_loc"]
            db.session.commit()
            flash(f"Location is Successfully Updated to '{ loc_present.loc_name }' ","success")
        if 'loc_name' in request.form:
            loc_name = request.form["loc_name"]
            loc_name = loc_name.capitalize()
            if Location.query.filter_by(loc_name=loc_name).first():
                flash(f"'{loc_name}' already exists in the records! ", "warning")
            else:
                new_location = Location(loc_name = loc_name)
                db.session.add(new_location)
                db.session.commit()
                flash(f"Location '{new_location}' is Saved Successfully!!! ","success")
    locations = Location.query.all()
    return render_template("location.html",locations = locations)


@app.route("/product_movement",methods =["GET","POST"] )
def movement():
    if request.method == "POST":
        if 'product_id' in request.form:
            #product_name = None
            #product_qty=None
            add = True
            from_location = request.form["from_location"]
            to_location= request.form["to_location"]       
                          
            if from_location != 'Choose...' or to_location != 'Choose...':
                if from_location == to_location:
                    add = False
                    flash('From and To location can not be same!', 'warning')
            else:
                flash("From and To locations were not selected!", 'warning')
                add = False


            if request.form["product_name"] == "Choose...":
                    flash("Please select a product!","warning")     
                    add = False   
            else:
                product_name = request.form["product_name"]
                if request.form["product_qty"] != None:
                    if int(request.form["product_qty"]) > 0:
                        product_qty = request.form["product_qty"]
                    if from_location != "Choose...":
                        total_items = get_tot(product_name,from_location)
                        if total_items == 0:
                            flash(f"{ product_name } is not available at { from_location }","warning")
                            add = False
                        elif int(product_qty) > total_items:
                            flash(f"Exceeds available quantity that is  { total_items } only","warning")
                            add = False
                        elif from_location != to_location:
                            int(product_qty) == total_items
                            add = True 
                            
                
                    
            if add:    
                
                from_location = request.form["from_location"]
                to_location = request.form["to_location"]
                product_name = request.form["product_name"]
                product_id = request.form["product_id"]
                product_qty = request.form["product_qty"]
                movement = Movement(from_location = from_location,to_location = to_location,product_id = product_id,product_name=product_name,product_qty = product_qty )
                db.session.add(movement)
                db.session.commit()
                flash("Movement is Successfully Saved","success")
        if 'edit_move' in request.form:
            edit = True
            movement_id = request.form['edit_move']
            movement = Movement.query.filter_by(_id=movement_id).first()
            new_qty = int(request.form["product_qty"])
            movement_pro = movement.product_name
            movement_from = movement.from_location
            movement_to = movement.to_location
            
            
            if request.form["product_qty"] != None:
                if int(new_qty) > 0:
                    new_qty = request.form["product_qty"]
                    
                if movement_from != "Choose...":
                    total_items = get_tot(movement_pro,movement_from)
                    if int(new_qty) == 0:
                        flash(f"Quantity cannot be zero","warning")
                        edit = False 
                    elif total_items == 0:
                        flash(f" { movement_pro }is not available at { movement_from } ","warning")
                        edit = False
                    elif int(new_qty) > total_items:
                        flash(f"Exceeds available quantity that is  { total_items } only","warning")
                        edit = False    
                    elif int(new_qty) < total_items:
                        edit = True
                    elif int(new_qty) == total_items:
                        edit = True


            if edit:
                movement.product_qty = new_qty
                db.session.commit()
                flash(f"Movement is Updated Successfully","success")
        return redirect('/product_movement')

    movements = Movement.query.all()
    return render_template("product_movement.html",movements =movements,products= Product.query.all(),locations = Location.query.all())


@app.route("/Report")
def Report(tag=None,order= None):
    msg= ''
    
    if 'str' in request.args:
        tag = request.args.get("str").capitalize()
        
    inv = balance(tag)
    
    if request.args:
        if not inv:
            msg = Markup("<h4>No such data is found!</h4>")
    elif not inv:
        msg = Markup("<h4>There's currently no data to display. Add now!</h4>")
    
    return render_template("Report.html",balance = inv,msg=msg)



def get_in(product,location):
    imported = Movement.query.filter_by(product_name=product).filter_by(to_location=location).all()
    return imported


def get_out(product,location):
    exported = Movement.query.filter_by(product_name=product).filter_by(from_location=location).all()
    return exported


def get_tot(product,location):
    imported = 0
    exported = 0
    imported_items = get_in(product,location)
    if imported_items:
        for item in imported_items:
            imported = imported + item.product_qty 
    exported_items = get_out(product,location)
    if exported_items:
        for item in exported_items:
            exported = exported + item.product_qty
    total = imported - exported
    return total

def balance(tag=None):
    balance=[]
    movements = Movement.query.all()
    if tag != None:
        products = Product.query.filter_by(pro_name = tag).all()
        locations = Location.query.all()
        if not products:
            locations = Location.query.filter_by(loc_name = tag).all()
            products = Product.query.all()
    else:
        products = Product.query.all()
        locations = Location.query.all()
    for location in locations:
        for product in products:
            inv = {}
            produ_name = product.pro_name
            loca_name = location.loc_name
            total = get_tot(produ_name,loca_name)
            inv['product'] = produ_name
            inv['location'] = loca_name
            if total == 0:
                continue
            else:
                inv['product_qty'] = total
            balance.append(inv)
    return balance
    

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)