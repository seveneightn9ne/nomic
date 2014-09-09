from flask import Flask, redirect, request, render_template, url_for
from flask.ext.mongoengine import MongoEngine

# from nomic.views import proposals, votes

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "nomic_db"}
app.config["SECRET_KEY"] = "super-secret"

db = MongoEngine(app)

from models import Proposal, Vote

# def register_blueprints(app):
#     # Prevents circular imports
#     from nomic.views import proposals, votes
#     app.register_blueprint(proposals)
#     app.register_blueprint(votes)

# register_blueprints(app)

# app.register_blueprint(proposals)
# app.register_blueprint(votes)

def get_sanitized_proposals():
    proposals = Proposal.objects(archived=False)
    for proposal in proposals:
        if not proposal.votes_revealed:
            for vote in proposal.votes:
                vote.vote = "[hidden]"
    return proposals

@app.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        return render_template('proposals/list.html', proposals=get_sanitized_proposals())
    else: # POST
        proposal = Proposal(created_by=request.form['created_by'], number=request.form['number'])
        proposal.save()

        return render_template('proposals/list.html', proposals=get_sanitized_proposals())

@app.route('/vote/<proposal_id>', methods=['POST'])
def add_vote(proposal_id):
    vote = Vote(name=request.form['name'], vote=request.form['vote'])
    proposal = Proposal.objects.get_or_404(id=proposal_id)

    existing_votes = filter(lambda v: v.name == vote.name, proposal.votes)
    if len(existing_votes) > 0:
        existing_vote = existing_votes[0]
        existing_vote.created_at = vote.created_at
        existing_vote.vote = vote.vote
    else:
        proposal.votes.append(vote)

    proposal.save()

    return redirect(url_for('list'))

@app.route('/archive/<proposal_id>')
def archive(proposal_id):
    proposal = Proposal.objects.get(id=proposal_id)
    proposal.archived = True
    proposal.save()

    return redirect(url_for('list'))

@app.route('/reveal/<proposal_id>')
def reveal(proposal_id):
    proposal = Proposal.objects.get(id=proposal_id)
    proposal.votes_revealed = True
    proposal.save()

    return redirect(url_for('list'))

if __name__ == "__main__":
    app.run()
