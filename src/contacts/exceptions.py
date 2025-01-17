class NewsFansNotFoundException(Exception):
    """
    get triggered manager Profile model
    can't find users who wants to get newsletter
    """

    pass


class LetterNotFoundException(Exception):
    """
    get triggered when there is no newsletter to send
    by cron jobs
    """

    pass


class JobError(Exception):
    """
    get triggered if sending newsletter by cron failed
    """

    pass


class HtmxFailureError(Exception):
    """
    get triggered if request is not htmx
    """

    pass
