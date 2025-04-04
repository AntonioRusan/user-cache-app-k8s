from flask import Flask, request, render_template, redirect, url_for
import redis
import uuid
from datetime import datetime
import os

app = Flask(__name__)

redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_password = os.getenv('REDIS_PASSWORD', '')

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True
)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        if name and email:
            user_id = str(uuid.uuid4())
            user_key = f"user:{user_id}"

            redis_client.hset(user_key, mapping={
                'id': user_id,
                'name': name,
                'email': email,
                'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            return redirect(url_for('index'))

    users = []
    # Ищем только ключи, начинающиеся с 'user:'
    for key in redis_client.scan_iter("user:*"):
        user_data = redis_client.hgetall(key)
        users.append(user_data)
    return render_template('index.html', users=users)


@app.route('/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    user_key = f"user:{user_id}"
    redis_client.delete(user_key)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)