FROM public.ecr.aws/lambda/python:3.12-arm64

# Copy fonts into container
COPY fonts/ /usr/share/fonts/truetype/dejavu/

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies (includes imageio-ffmpeg for moviepy)
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy function code
COPY deployed_backup/ ${LAMBDA_TASK_ROOT}/

# Copy background music
COPY deployed_backup/background_music.mp3 ${LAMBDA_TASK_ROOT}/background_music.mp3

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]

