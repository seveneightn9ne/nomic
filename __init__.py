from flask import Flask, redirect, request, render_template, url_for
from flask.ext.mongoengine import MongoEngine
from proxy import ReverseProxied
# from nomic.views import proposals, votes

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "nomic_db"}
app.wsgi_app = ReverseProxied(app.wsgi_app)

db = MongoEngine(app)

from models import Proposal, Vote

def get_sanitized_proposals():
    proposals = Proposal.objects(archived=False)
    for proposal in proposals:
        if not proposal.votes_revealed:
            for vote in proposal.votes:
                vote.vote = "[hidden]"
                vote.hate_upon = "[hidden]"
                vote.love = "[hidden]"
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
    vote = Vote(name=request.form['name'], vote=request.form['vote'], hate_upon=request.form['hate_upon'])
    proposal = Proposal.objects.get_or_404(id=proposal_id)

    existing_votes = filter(lambda v: v.name.lower().strip() == vote.name.lower().strip(), proposal.votes)
    if len(existing_votes) > 0:
        existing_vote = existing_votes[0]
        existing_vote.created_at = vote.created_at
        existing_vote.vote = vote.vote
        existing_vote.hate_upon = vote.hate_upon
        existing_vote.love = vote.love
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
