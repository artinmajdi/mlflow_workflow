# %% ---------------------------------------------------------------------------------------------------------------------
""" Importing the packages """
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"
from small_functions import architecture, loading_data, reading_terminal_inputs
import mlflow
import numpy as np

""" REMOTE postgres server: 
    Step 1 (before running the code): Connecting to remote server through ssh tunneling
        ssh -L 5000:128.196.142.22:5432 artinmajdi@128.196.142.22

    Step 2 (after running the code): Connecting to remote postgres server
        mlflow ui --backend-store-uri postgresql://mlflow_developer:1234@localhost:5000/mlflow_db --port 6789 
        
    Run from github:
        export MLFLOW_TRACKING_URI=http://127.0.0.1:{port} # port: 6789 or 5000
        mlflow run --no-conda --experiment-id experiment_id -P epoch=2 https://github.com/artinmajdi/mlflow_workflow.git -v main
        
        mlflow ui --backend-store-uri postgresql://mlflow_developer:1234@localhost:5000/mlflow_db  --default-artifact-root sftp://artinmajdi:Rtn1371369!@128.196.142.27:/home/artinmajdi/mlflow/artifact_store --port 6789


"""

# %% ---------------------------------------------------------------------------------------------------------------------
""" Reading the inputs fed through the command line """
# epochs, batch_size = reading_terminal_inputs()
epochs, batch_size = 3,32


# %% ---------------------------------------------------------------------------------------------------------------------
""" MLflow settings: 
        The style we should use when running mlflow ui
            Postgres server: server = f'{dialect_driver}://{username}:{password}@{ip}/{database_name}' 
            Local:           server = "file:/Users/artinmac/Documents/Research/Data7/mlflow/mlrun_store" """

username = 'mlflow_developer'
password = '1234'
port = '5000'
ip = 'localhost'
database_name = 'mlflow_db'
dialect_driver = 'postgresql'

server = f'{dialect_driver}://{username}:{password}@{ip}:{port}/{database_name}'

# TODO run it for cyverse as artifact



# %% ---------------------------------------------------------------------------------------------------------------------
""" Setting up the artifact server """ 
artifact_server = 'cyverse'

Artifacts = {
    'local':      "file:/Users/artinmac/Documents/Research/Data7/mlflow/artifact_store",
    'hpc':        'sftp://mohammadsmajdi@filexfer.hpc.arizona.edu:/home/u29/mohammadsmajdi/projects/mlflow/artifact_store',
    'atmosphere': 'sftp://artinmajdi:Rtn1371369!@128.196.142.27:/home/artinmajdi/mlflow/artifact_store',
    'cyverse': 'file:/Volumes/artinmajdi/projects/mlflow/artifact_store'}

artifact = Artifacts[artifact_server]

mlflow.set_tracking_uri(server)
# mlflow.set_registry_uri(server)


# %% ---------------------------------------------------------------------------------------------------------------------
""" Creating/Setting the experiment """
ExperimentName = {
    'local':      '/exp_final_artifact_local',
    'hpc':        '/exp_final_artifact_hpc',
    'atmosphere': '/exp_final_artifact_atmosphere',
    'cyverse':    '/exp_final_artifact_cyverse2'}

experiment_name = ExperimentName[artifact_server]

""" Line below should be commented if the experiment is already created
    If kept commented during the first run of a new experiment, the set_experiment 
    will automatically create the new experiment with local artifact storage """
# mlflow.create_experiment(name=experiment_name, artifact_location=artifact)
mlflow.set_experiment(experiment_name=experiment_name)

""" Loading the optimization parameters aturomatically from keras """
mlflow.keras.autolog()

mlflow.start_run()


# %% ---------------------------------------------------------------------------------------------------------------------
""" Model optimization """
model = architecture()

(train_images, train_labels), (test_images, test_labels) = loading_data()

""" model training and evaluation """
# with mlflow.start_run() as f:  # run_name='run_postgres_r2'experiment_id='7'
history = model.fit(train_images, train_labels, epochs=epochs, batch_size=batch_size,
                    validation_data=(test_images, test_labels))


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
mlflow.log_param("batch_size", batch_size)
mlflow.log_metric("test_acc", test_acc)
mlflow.log_metric("test_loss", test_loss)

mlflow.keras.log_model(model, "my_model_log")
# mlflow.keras.save_model(model, 'my_model')



#
# mlflow.log_artifact('predictions.txt')

# client.create_registered_model(description='first registered model', name=experiment_name)

print("Model saved in run %s" % mlflow.active_run().info.run_uuid)


# %% ---------------------------------------------------------------------------------------------------------------------
