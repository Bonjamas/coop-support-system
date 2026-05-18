from flask import request
from utils.search import apply_search
from utils.sort import apply_sort

TICKETS_PER_PAGE = 25


def build_listing(query):
    query = apply_search(query)
    query = apply_sort(query)
    page = max(request.args.get("page", 1, type=int), 1)
    return query.paginate(page=page, per_page=TICKETS_PER_PAGE, error_out=False)


def query_args(**overrides):
    args = request.args.to_dict()
    args.update(overrides)
    return args
