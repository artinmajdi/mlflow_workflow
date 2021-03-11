# %% ---------------------------------------------------------------------------------------------------------------------
""" Importing the packages """
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"
from small_functions import architecture, loading_data, reading_terminal_inputs
import mlflow
import numpy as np
from time import time
import git
 
# %% ---------------------------------------------------------------------------------------------------------------------
""" Reading the inputs fed through the command line """
epochs, batch_size = reading_terminal_inputs()
# epochs, batch_size = 3,32


# %% ---------------------------------------------------------------------------------------------------------------------
""" MLflow settings: 
        The style we should use when running mlflow ui
            Postgres server: server = f'{dialect_driver}://{username}:{password}@{ip}/{database_name}' 
            Local:           server = "file:/Users/artinmac/Documents/Research/Data7/mlflow/mlrun_store" """

postgres_connection_type = { 'direct':     ('5432', 'data7-db1.cyverse.org'),
                             'ssh-tunnel': ('5000', 'localhost')
                            }

port, host = postgres_connection_type['ssh-tunnel'] # 'direct' , 'ssh-tunnel'


username = "your-first-name" # e.g., nirav, hagan, nick, ...
password = '1234'
database_name = "project-name" # 'data7_lives_db' or 'data7_tbot_db'
dialect_driver = 'postgresql'

server = f'{dialect_driver}://{username}:{password}@{host}:{port}/{database_name}'

# %% ---------------------------------------------------------------------------------------------------------------------
""" Setting up the artifact server """ 
artifact_server = 'data7_db1'

Artifacts = {
    'local':      "file:/Users/artinmac/Documents/Research/Data7/mlflow/artifact_store",
    'hpc':        'sftp://mohammadsmajdi@filexfer.hpc.arizona.edu:/home/u29/mohammadsmajdi/projects/mlflow/artifact_store',
    'atmosphere': 'sftp://artinmajdi:{password}@128.196.142.4:/home/artinmajdi/mlflow/artifact_store',
    'cyverse':    'file:/Volumes/artinmajdi/projects/mlflow/artifact_store',
    'data7_db1':  'sftp://artinmajdi:temp_data7@data7-db1.cyverse.org:/home/artinmajdi/mlflow_data/artifact_store'}

artifact = Artifacts[artifact_server]

mlflow.set_tracking_uri(server)
# mlflow.set_registry_uri(server)

# %% ---------------------------------------------------------------------------------------------------------------------
""" Creating/Setting the experiment """
ExperimentName = {
    'local':      '/EXP_artifact_local',
    'hpc':        '/EXP_artifact_hpc',
    'atmosphere': '/EXP_artifact_atmosphere',
    'cyverse':    '/EXP_artifact_cyverse',
    'data7_db1':  f'/EXP_{username}'}

print('----------------------')
print(ExperimentName[artifact_server])
print('----------------------')


# artifact_server = 'local'
experiment_name = ExperimentName[artifact_server]

""" Line below should be commented if the experiment is already created
    If kept commented during the first run of a new experiment, the set_experiment 
    will automatically create the new experiment with local artifact storage """
mlflow.create_experiment(name=experiment_name, artifact_location=artifact)
mlflow.set_experiment(experiment_name=experiment_name)

""" Loading the optimization parameters aturomatically from keras """
mlflow.keras.autolog()

""" Starting the MLflow """
mlflow.start_run()


# %% ---------------------------------------------------------------------------------------------------------------------
""" Model optimization """
model = architecture()

(train_images, train_labels), (test_images, test_labels) = loading_data()

""" model training and evaluation """
# with mlflow.start_run() as f:  # run_name='run_postgres_r2'experiment_id='7'

start_time = time()
history = model.fit(train_images, train_labels, epochs=epochs, batch_size=batch_size, validation_data=(test_images, test_labels))
mlflow.log_metric("Time to optimize and save the model artifact", time()-start_time)

# %% ---------------------------------------------------------------------------------------------------------------------
""" Model evaluation """
test_loss, test_acc = model.evaluate(test_images, test_labels)
print('Accuracy:', test_acc)
print('Loss: ', test_loss)

prediction = model.predict(test_images)
predicted_classes = np.argmax(prediction, axis=1)


# %% ---------------------------------------------------------------------------------------------------------------------
""" Saving MLflow parameters & metrics """
mlflow.log_param("epochs", epochs)
mlflow.log_param("bsize", batch_size)
mlflow.log_metric("accuracy", test_acc)
mlflow.log_metric("test_loss", test_loss)

# mlflow.keras.log_model(model, "my_model_log")
# mlflow.keras.save_model(model, 'my_model')
# with open('predictions.txt', 'w') as f:
#     f.write("predicted_classes")
# mlflow.log_artifact('predictions.txt')
# client.create_registered_model(description='first registered model', name=experiment_name)

print("Model saved in run %s" % mlflow.active_run().info.run_uuid)
# %% ---------------------------------------------------------------------------------------------------------------------
mlflow.end_run()