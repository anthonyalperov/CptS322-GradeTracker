"use strict";

const gradeForm = document.getElementById("student-form");
const message = document.getElementById("message");
const gradesBody = document.getElementById("grades-body");
const progressContainer = document.getElementById("course-progress");
const dashboardContent = document.getElementById("dashboard-content");
const emptyState = document.getElementById("empty-state");
const submitButton = document.getElementById("lookup-button");
const chartFallback = document.getElementById("chart-fallback");
let courseChart = null;

function gradeLetter(score) {
    // Display scale for the dashboard; this is NOT an official institutional GPA scale.
    if (score >= 90) return "A";
    if (score >= 80) return "B";
    if (score >= 70) return "C";
    if (score >= 60) return "D";
    return "F";
}

function formatScore(value) {
    return Number(value).toFixed(1).replace(/\.0$/, "");
}

function setText(id, value) {
    document.getElementById(id).textContent = String(value);
}

function resetDashboard() {
    dashboardContent.hidden = true;
    emptyState.hidden = false;
    gradesBody.replaceChildren();
    progressContainer.replaceChildren();
    if (courseChart) {
        courseChart.destroy();
        courseChart = null;
    }
    chartFallback.hidden = true;
}

function courseSummaries(grades) {
    const groups = new Map();
    for (const grade of grades) {
        const score = Number(grade.score);
        if (!Number.isFinite(score) || score < 0 || score > 100) continue;
        const id = String(grade.course_id);
        if (!groups.has(id)) {
            groups.set(id, {
                name: String(grade.course_name || `Course ${id}`),
                sum: 0,
                count: 0,
            });
        }
        const course = groups.get(id);
        course.sum += score;
        course.count += 1;
    }
    return Array.from(groups.values()).map(course => ({
        name: course.name,
        average: course.sum / course.count,
        count: course.count,
    })).sort((a, b) => b.average - a.average);
}

function renderGradeTable(grades) {
    const fragment = document.createDocumentFragment();
    for (const grade of grades) {
        const score = Number(grade.score);
        if (!Number.isFinite(score) || score < 0 || score > 100) continue;
        const row = document.createElement("tr");
        const course = document.createElement("td");
        const value = document.createElement("td");
        const letter = document.createElement("td");
        course.textContent = String(grade.course_name || "Unknown course");
        value.textContent = `${formatScore(score)}%`;
        letter.textContent = gradeLetter(score);
        row.append(course, value, letter);
        fragment.appendChild(row);
    }
    gradesBody.appendChild(fragment);
}

function renderCourseBars(courses) {
    const fragment = document.createDocumentFragment();
    for (const course of courses) {
        const item = document.createElement("article");
        item.className = "course-progress-item";
        const heading = document.createElement("div");
        heading.className = "course-progress-heading";
        const name = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = course.name;
        const description = document.createElement("span");
        description.textContent = `${course.count} grade ${course.count === 1 ? "entry" : "entries"}`;
        name.append(title, description);
        const score = document.createElement("span");
        score.className = "course-score";
        score.textContent = `${formatScore(course.average)}% · ${gradeLetter(course.average)}`;
        heading.append(name, score);
        const track = document.createElement("div");
        track.className = "course-progress-track";
        track.setAttribute("role", "progressbar");
        track.setAttribute("aria-label", `${course.name} average`);
        track.setAttribute("aria-valuemin", "0");
        track.setAttribute("aria-valuemax", "100");
        track.setAttribute("aria-valuenow", formatScore(course.average));
        const fill = document.createElement("div");
        fill.className = "course-progress-fill";
        fill.style.width = `${Math.max(0, Math.min(100, course.average))}%`;
        track.append(fill);
        item.append(heading, track);
        fragment.appendChild(item);
    }
    progressContainer.appendChild(fragment);
}

function renderChart(courses) {
    if (typeof Chart === "undefined") {
        chartFallback.hidden = false;
        return;
    }
    const canvas = document.getElementById("course-chart");
    courseChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: courses.map(course => course.name),
            datasets: [{
                label: "Average grade (%)",
                data: courses.map(course => Number(course.average.toFixed(2))),
                backgroundColor: "rgba(157, 28, 47, 0.85)",
                hoverBackgroundColor: "#791426",
                borderRadius: 6,
                maxBarThickness: 65,
            }],
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {legend: {display: false}, tooltip: {callbacks: {
                label: context => `${context.parsed.y}% average`,
            }}},
            scales: {
                y: {beginAtZero: true, max: 100, ticks: {callback: value => `${value}%`}, grid: {color: "#eef0f3"}},
                x: {grid: {display: false}, ticks: {maxRotation: 35, minRotation: 0}},
            },
        },
    });
}

function renderDashboard(studentId, grades) {
    const validGrades = grades.filter(grade => Number.isFinite(Number(grade.score)) && Number(grade.score) >= 0 && Number(grade.score) <= 100);
    const courses = courseSummaries(validGrades);
    if (validGrades.length === 0) {
        message.textContent = "No grades are recorded for this student yet.";
        message.className = "student-message notice";
        return;
    }

    const average = validGrades.reduce((total, grade) => total + Number(grade.score), 0) / validGrades.length;
    setText("student-label", `Student #${studentId}`);
    setText("overall-average", formatScore(average));
    setText("course-count", courses.length);
    setText("overall-letter", gradeLetter(average));
    setText("grade-count", validGrades.length);
    setText("top-course", `${courses[0].name} · ${formatScore(courses[0].average)}%`);
    setText("average-insight", `${formatScore(average)}% (${gradeLetter(average)})`);
    setText("next-step", courses.length > 1 ? `Review ${courses[courses.length - 1].name}` : "Keep tracking your progress");

    renderCourseBars(courses);
    renderGradeTable(validGrades);
    renderChart(courses);
    emptyState.hidden = true;
    dashboardContent.hidden = false;
    message.textContent = "Dashboard loaded successfully.";
    message.className = "student-message success";
}

gradeForm.addEventListener("submit", async event => {
    event.preventDefault();
    const studentId = document.getElementById("student-id").value.trim();
    if (!/^\d+$/.test(studentId) || Number(studentId) < 1) {
        message.textContent = "Enter a valid positive student ID.";
        message.className = "student-message error";
        return;
    }
    resetDashboard();
    submitButton.disabled = true;
    submitButton.textContent = "Loading…";
    message.textContent = "Loading grades…";
    message.className = "student-message";

    try {
        const response = await fetch(`/students/${encodeURIComponent(studentId)}/grades`, {
            headers: {Accept: "application/json"},
        });
        if (!response.ok) {
            if (response.status === 404) throw new Error("Student not found. Check the student ID and try again.");
            throw new Error(`Couldn't load grades (HTTP ${response.status}). Please try again.`);
        }
        const data = await response.json();
        if (!data || !Array.isArray(data.grades)) throw new Error("Unexpected response from the server.");
        renderDashboard(studentId, data.grades);
    } catch (error) {
        message.textContent = error.message || "Unable to load grades.";
        message.className = "student-message error";
    } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = 'Load dashboard <span aria-hidden="true">→</span>';
    }
});
