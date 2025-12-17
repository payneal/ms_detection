import os
from flask import Flask, request, jsonify, send_file, abort, url_for
from ariadne import QueryType, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerGraphiQL

# ---- Config: only serve images from inside this folder ----
IMAGE_ROOT = os.path.abspath(os.environ.get("IMAGE_ROOT", "./data"))  # change to wherever you store outputs

type_defs = """
    type Query {
        imageUrl(path: String!): String!
    }
"""

query = QueryType()

def safe_join(root: str, user_path: str) -> str:
    """
    Prevent path traversal by forcing user_path to stay under root.
    """
    # normalize and remove leading slashes
    user_path = user_path.lstrip("/")

    full_path = os.path.abspath(os.path.join(root, user_path))
    if not full_path.startswith(root + os.sep) and full_path != root:
        raise ValueError("Invalid path")
    return full_path

@query.field("imageUrl")
def resolve_image_url(*_, path: str) -> str:
    # We return a URL that the browser can load
    # Example: /img?path=some_folder/slice_001.png
    return url_for("serve_img", path=path, _external=True)

schema = make_executable_schema(type_defs, query)

app = Flask(__name__)

# Optional: built-in GraphiQL UI for testing
graphiql = ExplorerGraphiQL(title="Image GraphQL")

@app.get("/graphql")
def graphql_playground():
    return graphiql.html(None), 200

@app.post("/graphql")
def graphql_server():
    data = request.get_json(force=True)
    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
        debug=True
    )
    status = 200 if success else 400
    return jsonify(result), status

@app.get("/img")
def serve_img():
    rel_path = request.args.get("path")
    if not rel_path:
        abort(400, "Missing ?path=")

    try:
        full_path = safe_join(IMAGE_ROOT, rel_path)
    except ValueError:
        abort(400, "Invalid path")

    if not os.path.isfile(full_path):
        abort(404, "File not found")

    # Basic extension allowlist (optional but recommended)
    ext = os.path.splitext(full_path)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg"}:
        abort(415, "Only PNG/JPG/JPEG allowed")

    # send_file will stream and set a reasonable Content-Type
    return send_file(full_path)

if __name__ == "__main__":
    os.makedirs(IMAGE_ROOT, exist_ok=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
