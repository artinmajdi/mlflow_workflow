import os

os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"
from small_functions import architecture, loading_data, reading_terminal_inputs
import mlflow
import numpy as np

epochs, batch_size = reading_terminal_inputs()

username = 'mlflow_developer'
password = '1234'
port     = '5000'

# Atmosphere:        '172.29.207.12'
# Ubuntu-Laptop:     '192.168.0.19'
# localhost:         '127.0.0.1'
# Data7 workstation: '10.208.16.20'
# My MacOS           '192.168.0.13'
ip       = '192.168.0.19'
database_name  = 'mlflow_db'
dialect_driver = 'postgresql'

""" below is the style we should use when running mlflow ui
    server = f'{dialect_driver}://{username}:{password}@{ip}/{database_name}' """

server = f'{dialect_driver}://{username}:{password}@{ip}/{database_name}' # :{port}
# server   = "file:/Users/artinmac/Documents/Research/Data7/mlflow/mlrun_store"

# artifact = "file:/Users/artinmac/Documents/Research/Data7/mlflow/artifact_store"
artifact = 'sftp://mohammadsmajdi@filexfer.hpc.arizona.edu:/home/u29/mohammadsmajdi/mlflow/artifact_store'

mlflow.set_tracking_uri(server)
# mlflow.set_registry_uri(server)

""" Creating experiment """
experiment_name = '/experiment_Server_remotepostgres_data7_Artifact_HPC'
mlflow.create_experiment(name=experiment_name , artifact_location=artifact)

""" Setting the experiment """
mlflow.set_experiment(experiment_name=experiment_name)

mlflow.keras.autolog()

if __name__ == "__main__":
    model = architecture()

    (train_images, train_labels), (test_images, test_labels) = loading_data()

    with mlflow.start_run(run_name='run_postgres_r2') as f:  # experiment_id='7'
        history = model.fit(train_images, train_labels, epochs=epochs, batch_size=batch_size,
                            validation_data=(test_images, test_labels))

        test_loss, test_acc = model.evaluate(test_images, test_labels)
        print('Accuracy:', test_acc)
        print('Loss: ', test_loss)

        prediction = model.predict(test_images)
        predicted_classes = np.argmax(prediction, axis=1)

        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_metric("test_acc", test_acc)
        mlflow.log_metric("test_loss", test_loss)

        # mlflow.keras.log_model(model, "my_model_log")
        # mlflow.keras.save_model(model, 'my_model')

        # with open('predictions.txt', 'w') as f:
        #     f.write("predicted_classes")
        #
        # mlflow.log_artifact('predictions.txt')

        # client.create_registered_model(description='first registered model', name=experiment_name)

        print("Model saved in run %s" % mlflow.active_run().info.run_uuid)