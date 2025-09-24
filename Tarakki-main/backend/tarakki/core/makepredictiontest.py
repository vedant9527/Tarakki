from .models import StudentProfile
import joblib

loaded_mlp = joblib.load('mlp_model.pkl')
scaler = joblib.load('scaler.pkl')
label_encoder = joblib.load('label_encoder.pkl')

def get_scores(user):
    try:
        # Fetch the student profile for the given user
        profile = StudentProfile.objects.get(user=user)
        # Retrieve the scores field from the profile
        scores_array = profile.scores
        return scores_array
    except StudentProfile.DoesNotExist:
        # If the profile does not exist, return an empty array or handle the error accordingly
        return []
    
def makeprediction(user):
    # Get scores from the student's profile
    scores_array = get_scores(user)

    # Check if the scores exist
    if scores_array is None:
        return "No scores available for this user."

    try:
        # Ensure the input matches the model's expected format
        sample_input = [scores_array]

        # Scale the input using the same scaler used during training
        sample_input_scaled = scaler.transform(sample_input)

        # Make the prediction
        predicted_career = loaded_mlp.predict(sample_input_scaled)

        # Decode the predicted label back to the original class
        predicted_career_label = label_encoder.inverse_transform(predicted_career)

        # Return the predicted career
        return f'Predicted Career: {predicted_career_label[0]}'
    except Exception as e:
        return f"Error in prediction: {str(e)}"