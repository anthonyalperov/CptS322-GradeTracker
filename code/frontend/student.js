
const form = document.getElementById("student-form");
const message = document.getElementById("message");
const gradesSection = document.getElementById("grades-section");
const gradesBody = document.getElementById("grades-body");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const studentId = document.getElementById("student-id").value;

    message.textContent = "";
    gradesBody.replaceChildren();
    gradesSection.hidden = true;

    try {
        const response = await fetch(`/students/${studentId}/grades`);

        if (!response.ok) {
            throw new Error("Unable to load student grades.");
        }

        const data = await response.json();
        const grades = data.grades;

        
        if (grades.length === 0) {
            message.textContent = "No grades found for this student.";
            return;
        }

        grades.forEach((grade) => {
            const row = document.createElement("tr");

            const courseCell = document.createElement("td");
            courseCell.textContent = grade.course_name;

            const scoreCell = document.createElement("td");
            scoreCell.textContent = `${grade.score}%`;

            row.append(courseCell, scoreCell);
            gradesBody.appendChild(row);
        });

        gradesSection.hidden = false;
    } catch (error) {
        message.textContent = error.message;
    }
});