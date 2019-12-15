import time
from flask import *
from sqlalchemy import *

from ruqqus.helpers.wrappers import *

from ruqqus.__main__ import app, db, cache
from ruqqus.classes.submission import Submission


@cache.memoize(timeout=600)
def trending_boards(n=5):

    boards=db.query(Board).filter_by(is_banned=False).order_by(text("boards.trending_rank desc")).limit(n)

    return [x for x in boards]

@cache.memoize(timeout=600)
def frontlist(sort="hot", page=1, nsfw=False):

    #cutoff=int(time.time())-(60*60*24*30)

    posts = db.query(Submission).filter_by(is_banned=False,
                                           is_deleted=False,
                                           stickied=False)

    if not nsfw:
        posts=posts.filter_by(over_18=False)

    if sort=="hot":
        posts=posts.order_by(text("submissions.rank_hot desc"))
    elif sort=="new":
        posts=posts.order_by(Submission.created_utc.desc())
    elif sort=="disputed":
        posts=posts.order_by(text("submissions.rank_fiery desc"))
    elif sort=="top":
        posts=posts.order_by(text("submissions.score desc"))
    elif sort=="activity":
        posts=posts.order_by(text("submissions.rank_activity desc"))
    else:
        abort(422)

    posts=[x.id for x in posts.offset(25*(page-1)).limit(26).all()]
    

    return posts
    


@app.route("/", methods=["GET"])
@auth_desired
def home(v):

    page=int(request.args.get("page",1))

    #prevent invalid paging
    page=max(page, 1)

    sort_method=request.args.get("sort", "hot")

    #get list of ids
    ids = frontlist(sort=sort_method, page=page, nsfw=(v and v.over_18))

    #check existence of next page
    next_exists=(len(ids)==26)
    ids=ids[0:25]

    #check if ids exist
    if ids:
        #assemble list of tuples
        i=1
        tups=[]
        for x in ids:
            tups.append((x, i))
            i+=1

        #tuple string
        tups = str(tups).lstrip("[").rstrip("]")
            

        #hit db for entries
        
        posts=db.query(Submission
                       ).from_statement(
                           text(f"""
                            select submissions.*, submissions.ups, submissions.downs
                            from submissions
                            join (values {tups}) as x(id, n) on submissions.id=x.id order by x.n"""
                                )).all()
    else:
        posts=[]

    

    #If page 1, check for sticky
    if page==1:
        sticky =[]
        sticky=db.query(Submission).filter_by(stickied=True).first()
        if sticky:
            posts=[sticky]+posts
    
    return render_template("home.html", v=v, listing=posts, next_exists=next_exists, sort_method=sort_method, page=page)


@app.route("/guilds", methods=["GET"])
@auth_required
def home_subs(v):

    return v.rendered_subscription_page(sort=request.args.get("sort","hot"),
                                        page=max(int(request.args.get("page",1)),0)
                                        )

@app.route("/subscriptions", methods=["GET"])
@auth_required
def user_subs(v):

    return v.rendered_follow_page(sort=request.args.get("sort","hot"),
                                  page=max(int(request.args.get("page",1)),0)
                                  )

