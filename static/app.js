// ============================================================
// TouchGrass-AI Frontend
// ============================================================


const form =
    document.getElementById("guideForm");


const result =
    document.getElementById("result");


const errorBox =
    document.getElementById("error");


const generateBtn =
    document.getElementById("generateBtn");


const buttonText =
    document.getElementById("buttonText");


const loader =
    document.getElementById("loader");


// ============================================================
// Form Submit
// ============================================================

form.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        hideError();

        result.classList.add("hidden");

        setLoading(true);


        // ----------------------------------------------------
        // Collect user input
        // ----------------------------------------------------

        const data = {

            location:
                document
                    .getElementById("location")
                    .value
                    .trim(),

            activity:
                document
                    .getElementById("activity")
                    .value,

            duration:
                document
                    .getElementById("duration")
                    .value,

            fitness:
                document
                    .getElementById("fitness")
                    .value,

            preferences:
                document
                    .getElementById("preferences")
                    .value
                    .trim(),

            constraints:
                document
                    .getElementById("constraints")
                    .value
                    .trim()
        };


        // ----------------------------------------------------
        // Validate
        // ----------------------------------------------------

        if (!data.location) {

            showError(
                "Please enter your area."
            );

            setLoading(false);

            return;
        }


        if (!data.activity) {

            showError(
                "Please choose an outdoor activity."
            );

            setLoading(false);

            return;
        }


        // ----------------------------------------------------
        // Call FastAPI
        // ----------------------------------------------------

        try {

            const response =
                await fetch(
                    "/api/guide",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(data)
                    }
                );


            let responseData;


            try {

                responseData =
                    await response.json();

            } catch {

                throw new Error(
                    "The server returned an invalid response."
                );

            }


            // ------------------------------------------------
            // HTTP error
            // ------------------------------------------------

            if (!response.ok) {

                throw new Error(
                    responseData.detail ||
                    "Failed to generate guide."
                );

            }


            // ------------------------------------------------
            // Validate application response
            // ------------------------------------------------

            if (
                !responseData.success ||
                !responseData.guide
            ) {

                throw new Error(
                    "The AI returned an unexpected response."
                );

            }


            // ------------------------------------------------
            // Render
            // ------------------------------------------------

            renderGuide(
                responseData.guide
            );


        } catch (error) {

            console.error(
                "TouchGrass-AI error:",
                error
            );


            showError(
                error.message ||
                "Something went wrong."
            );


        } finally {

            setLoading(false);

        }

    }
);


// ============================================================
// Render Guide
// ============================================================

function renderGuide(guide) {


    // --------------------------------------------------------
    // Title
    // --------------------------------------------------------

    document
        .getElementById("guideTitle")
        .textContent =
            guide.title ||
            "Your outdoor adventure";


    // --------------------------------------------------------
    // Summary
    // --------------------------------------------------------

    document
        .getElementById("guideSummary")
        .textContent =
            guide.summary ||
            "";


    // --------------------------------------------------------
    // Activity
    // --------------------------------------------------------

    const activity =
        guide.activity || {};


    document
        .getElementById("activityName")
        .textContent =
            activity.name ||
            "Outdoor activity";


    document
        .getElementById("whyItFits")
        .textContent =
            activity.why_it_fits ||
            "";


    document
        .getElementById("difficulty")
        .textContent =
            activity.difficulty ||
            "Easy";


    document
        .getElementById("durationResult")
        .textContent =
            activity.duration ||
            "";


    document
        .getElementById("bestTime")
        .textContent =
            activity.best_time ||
            "";


    // --------------------------------------------------------
    // Plan
    // --------------------------------------------------------

    renderList(
        document.getElementById("plan"),
        guide.plan
    );


    // --------------------------------------------------------
    // What to bring
    // --------------------------------------------------------

    renderList(
        document.getElementById("whatToBring"),
        guide.what_to_bring
    );


    // --------------------------------------------------------
    // Safety
    // --------------------------------------------------------

    renderList(
        document.getElementById("safety"),
        guide.safety
    );


    // --------------------------------------------------------
    // Challenge
    // --------------------------------------------------------

    document
        .getElementById("challenge")
        .textContent =
            guide.touch_grass_challenge ||
            "Spend some time outside without checking your phone.";


    // --------------------------------------------------------
    // Offline tip
    // --------------------------------------------------------

    document
        .getElementById("offlineTip")
        .textContent =
            guide.offline_tip ||
            "Read the plan once, remember the important parts, and put your phone away.";


    // --------------------------------------------------------
    // Show result
    // --------------------------------------------------------

    result.classList.remove(
        "hidden"
    );


    // --------------------------------------------------------
    // Scroll to result
    // --------------------------------------------------------

    setTimeout(
        function () {

            result.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        },
        100
    );

}


// ============================================================
// Render Lists
// ============================================================

function renderList(
    element,
    items
) {

    element.innerHTML = "";


    if (!Array.isArray(items)) {

        return;

    }


    items.forEach(
        function (item) {

            const li =
                document.createElement("li");


            li.textContent =
                String(item);


            element.appendChild(
                li
            );

        }
    );

}


// ============================================================
// Loading State
// ============================================================

function setLoading(
    loading
) {

    generateBtn.disabled =
        loading;


    if (loading) {

        buttonText.textContent =
            "Generating your adventure...";


        loader.classList.remove(
            "hidden"
        );

    } else {

        buttonText.textContent =
            "🌱 Generate My TouchGrass Plan";


        loader.classList.add(
            "hidden"
        );

    }

}


// ============================================================
// Show Error
// ============================================================

function showError(
    message
) {

    document
        .getElementById("errorMessage")
        .textContent =
            message;


    errorBox.classList.remove(
        "hidden"
    );


    errorBox.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


// ============================================================
// Hide Error
// ============================================================

function hideError() {

    errorBox.classList.add(
        "hidden"
    );

}
