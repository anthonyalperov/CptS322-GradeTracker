
const gradeForm = document.getElementById("grade-form");
const message = document.getElementById("message");

gradeForm.addEventListener("submit", async (event) => {
    // Prevent the page from refreshing when submitted.
    event.preventDefault();

    // Get the values entered by the instructor.
    const gradeId = Number(document.getElementById("grade-id").value);
    const instructorId = Number(document.getElementById("instructor-id").value);
    const score = Number(document.getElementById("score").value);

    // Reset the previous message.
    message.textContent = "Updating grade...";
    message.className = "";

    const submitButton = gradeForm.querySelector("button");
    submitButton.disabled = true;

    try {
        // Send the grade update to our FastAPI backend.
        const response = await fetch(`/grades/${gradeId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                instructor_id: instructorId,
                score: score
            })
        });

        const data = await response.json();

        if (!response.ok) {
            // Display an error returned by FastAPI.
            const error = typeof data.detail === "string"
                ? data.detail
                : "Unable to update grade.";

            throw new Error(error);
        }

        // Show confirmation when the update succeeds.
        message.textContent = `Grade #${gradeId} updated to ${score}.`;
        message.className = "success";

        // Clear the form after a successful update.
        gradeForm.reset();

    } catch (error) {
        message.textContent = `Error: ${error.message}`;
        message.className = "error";

    } finally {
        // Allow another submission.
        submitButton.disabled = false;
    }
});
