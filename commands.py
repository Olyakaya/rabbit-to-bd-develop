from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import scoped_session

import db
import models


if db.isConnected:
    Session = scoped_session(db.session_factory)


def addUserCommand(data) -> models.User:
    """
    The function return User records from the db.

    :param data: JSON
    :return: User from models
    """
    user = models.User(UserId=data.issue.user.login,
                       HtmlUrl=data.issue.user.html_url,
                       AvatarUrl=data.issue.user.avatar_url)
    query = Session.query(models.User).filter(models.User.UserId == user.UserId)
    return addObjCommand(user, query)


def addActionCommand(data) -> models.Action:
    """
    The function return Action records from the db.

    :param data: JSON
    :return: Action from models
    """
    action = models.Action(Title=data.action)
    query = Session.query(models.Action).filter(models.Action.Title == action.Title)
    return addObjCommand(action, query)


def addStateCommand(data) -> models.State:
    """
    The function return State records from the db.

    :param data: JSON
    :return: State from models
    """
    state = models.State(Title=data.issue.state)
    query = Session.query(models.State).filter(models.State.Title == state.Title)
    return addObjCommand(state, query)


def addLabelsCommand(data) -> [models.Label]:
    """
    The function return list of Labels records from the db.

    :param data: JSON
    :return: list Label from models
    """
    labels = []
    for item in data.issue.labels:
        label = models.Label(Title=item.name)
        query = Session.query(models.Label).filter(models.Label.Title == label.Title)
        labels.append(addObjCommand(label, query))
    return labels


def addIssueCommand(data) -> models.Issue:
    """
    The function return Issue record from the db.

    :param data: JSON
    :return: Issue from models
    """
    issue = models.Issue(IssueId=data.issue.id,
                         HtmlUrl=data.issue.html_url,
                         Number=data.issue.number,
                         Title=data.issue.title,
                         Body=data.issue.body)
    query = Session.query(models.Issue).filter(models.Issue.IssueId == issue.IssueId)
    return addObjCommand(issue, query)


def addIssueActionCommand(data, user, action) -> models.IssueAction:
    """
    The function return IssueActions record from the db.

    :param data: JSON
    :param action: Action from models
    :param user: User from models
    :return: IssueAction from models
    """

    issueAction = models.IssueAction(IssueId=data.issue.id,
                                     ActionId=action.ActionId,
                                     UserId=user.UserId,
                                     ModifiedDate=data.issue.data)

    query = Session.query(models.IssueAction).filter((models.IssueAction.IssueId == issueAction.IssueId)
                                                     & (models.IssueAction.ActionId == issueAction.ActionId)
                                                     & (models.IssueAction.ModifiedDate == issueAction.ModifiedDate))
    return addObjCommand(issueAction, query)


def addIssueStateCommand(data, state) -> models.IssueState:
    """
    The function return IssueState record from the DB.

    :param data: JSON
    :param state: IssueState from models
    :return: IssueState from models
    """

    issueState = models.IssueState(IssueId=data.issue.id,
                                   StateId=state.StateId,
                                   ModifiedDate=data.issue.data)

    query = Session.query(models.IssueState).filter(and_(models.IssueState.IssueId == issueState.IssueId,
                                                         models.IssueState.StateId == issueState.StateId,
                                                         models.IssueState.ModifiedDate == issueState.ModifiedDate))
    return addObjCommand(issueState, query)


def addIssueLabelsCommand(data, labels: [models.Label]) -> [models.IssueLabel]:
    """
    The function return IssueLabels record from the DB.

    :param data: JSON
    :param labels: The list of Labels
    :return: List of Labels
    """
    issueLabels = []
    for label in labels:
        issueLabel = models.IssueLabel(IssueId=data.issue.id,
                                       LabelId=label.LabelId)
        query = Session.query(models.IssueLabel).filter((models.IssueLabel.IssueId == issueLabel.IssueId)
                                                        & (models.IssueLabel.LabelId == issueLabel.LabelId))
        issueLabels.append(addObjCommand(issueLabel, query))
    return issueLabels


def addObjCommand(obj, query):
    """
    The function return obj record from the db.

    :param obj: The model instance
    :param query: Query to DB
    :return: object from DB
    """
    try:
        obj = query.one()
        print(f"Function addObjCommand() - {obj} exist")
    except NoResultFound:
        Session.add(obj)
        print(f"Function addObjCommand() - {obj} added")
    finally:
        Session.commit()
        print(f"{obj}")
    return obj


def addNewIssueToDB(data):
    """
    The function checks for the existence of a User, Issue,
    Action, State, Label records in the db, if there is none,
    the records is added. And adds records to the IssueAction,
    IssueState, IssueLabel tables.

    :param data: JSON
    :return: None
    """

    if data.action == 'opened' and not isIssueExist(data.issue.id):
        user = addUserCommand(data)
        issue = addIssueCommand(data)
        action = addActionCommand(data)
        state = addStateCommand(data)
        labels = addLabelsCommand(data)
        issueAction = addIssueActionCommand(data, user, action)
        issueState = addIssueStateCommand(data, state)
        issueLabels = addIssueLabelsCommand(data, labels)


def updateIssue(data):
    if not data.action == 'opened' and isIssueExist(data.issue.id):
        user = addUserCommand(data)
        action = addActionCommand(data)
        state = addStateCommand(data)
        issueAction = addIssueActionCommand(data, user, action)
        issueState = addIssueStateCommand(data, state)


def isIssueExist(issueId) -> bool:
    isExist = False
    query = Session \
        .query(models.Issue) \
        .filter(models.Issue.IssueId == issueId)
    try:
        query.one()
        isExist = True
    except NoResultFound:
        isExist = False
    finally:
        Session.commit()
        return isExist
