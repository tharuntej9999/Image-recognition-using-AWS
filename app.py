from flask import Flask, request, render_template
import boto3

app = Flask(__name__)
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
sns_client = boto3.client('sns')

# Replace with your S3 bucket name
S3_BUCKET = 'your-s3-bucket-name'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No image part"
    
    image_file = request.files['image']

    if image_file.filename == '':
        return "No selected image file"
    
    # Upload the image to S3
    s3_client.upload_fileobj(image_file, S3_BUCKET, image_file.filename)

    # Perform image recognition using Rekognition
    response = rekognition_client.detect_labels(
        Image={'S3Object': {'Bucket': S3_BUCKET, 'Name': image_file.filename}}
    )

    labels = [label['Name'] for label in response['Labels']]

    # Send an SNS notification
    sns_client.publish(
        TopicArn='your-sns-topic-arn',
        Message=f"Uploaded image: {image_file.filename}, Labels: {', '.join(labels)}"
    )

    return f"Image uploaded and recognized. Labels: {', '.join(labels)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)