# Event Architect AI — Complete Rebuild Specification

## 1. Your Role

Act as a senior Python software engineer, Streamlit application architect, data visualization specialist, and enterprise UX designer.

Rebuild the existing **Event Architect AI** application from the ground up.

The current application has a dark interface and a venue visualization, but the venue appears as a basic coordinate chart with colored rectangles. Visitor dots overlap around the entrance, facility labels are difficult to read, and the overall interface resembles a development prototype rather than a professional event-planning platform.

Do not merely adjust colors, fonts, or card styles. Redesign the application structure, visualization system, interaction model, and analytical workflow.

The final result must be a functional, polished, responsive, Korean-language web application built primarily with Python and Streamlit.

**GitHub is the source repository, and Streamlit is the application framework. Do not migrate the project to React, Next.js, TypeScript, or a separate frontend framework.**

## 2. Mandatory First Step: Inspect the Repository

Before writing code:

1. Inspect the complete repository and identify its existing directory structure.
2. Read `requirements.txt`, `pyproject.toml`, or other dependency files, along with the Streamlit entry point and deployment configuration.
3. Identify the current application entry point, existing modules, available assets, data files, and secrets/configuration requirements.
4. Determine whether the current project is deployed through Streamlit Community Cloud or another Streamlit-compatible environment.
5. Identify reusable functionality and any dependencies that should be retained.
6. Create a concise implementation plan, then implement the rebuild.

Do not assume the main file is named `app.py`. Verify the actual entry point.

Keep the application compatible with the existing GitHub repository and Streamlit deployment workflow. Do not introduce unnecessary dependencies or require paid services, external APIs, API keys, or a database server for the basic prototype.

## 3. Product Vision

Event Architect AI is an AI-assisted inclusive event-planning platform.

Its purpose is to help organizers design safer, more accessible, and more efficient events before they take place.

The application should accept event conditions, generate alternative venue layouts, simulate estimated visitor movement, evaluate congestion and accessibility, compare alternatives, and explain its recommendations.

The target users include school festival organizers, local event planners, exhibition organizers, and community event operators.

The interface must communicate three things immediately:

* What the event venue looks like.
* Where potential congestion and accessibility problems exist.
* How the proposed design improves the event compared with the original layout.

Do not build a generic analytics dashboard with an unrelated chart collection. Every visualization must support an event-planning decision.

## 4. Technology Requirements

Use the following architecture:

* Python for application logic.
* Streamlit for the web interface and interactions.
* Plotly for interactive venue maps, heatmaps, and analytical charts.
* Pandas and NumPy for data processing and simulation calculations.
* Streamlit session state for interactive application state.
* Local JSON or CSV files for optional sample data and configuration.

Use the existing compatible dependencies where possible.

Do not add a machine-learning framework simply to make the application look AI-powered.

Implement a transparent, deterministic layout-generation and scoring engine for the initial prototype. If an actual trained AI model is not available, describe the feature as AI-assisted optimization based on rules and scoring. Do not falsely claim that a real AI model has been trained.

Keep simulation logic separate from UI rendering so that it can be tested independently.

## 5. Application Layout

Create a premium desktop-first enterprise interface with responsive behavior.

### A. Sidebar

Create a compact, consistent sidebar with the product name:

**Event Architect AI**

Subtitle: Inclusive Event Planning Platform

Navigation items:

1. Dashboard
2. Event Design
3. Digital Twin
4. AI Simulation
5. AI Report
6. Settings

Use appropriate icons and clear active-navigation styling.

Each navigation item must open its corresponding functional page or view. Do not create menu items that do nothing.

Include a small status indicator showing whether the current data is sample data or user-configured data.

### B. Top Header

Include:

* Current page title and concise description.
* Event name.
* Simulation status.
* Primary action button.
* A compact event selector if multiple events are supported.

Avoid oversized headers and excessive decorative elements.

### C. Main Workspace

The Dashboard should prioritize the venue visualization.

Use this general desktop composition:

* Main venue workspace: approximately 65–70% of the available content width.
* Right-side analysis panel: approximately 30–35%.
* Compact summary metrics above the workspace.
* Detailed analytics below the workspace.

Avoid excessive whitespace, giant KPI cards, horizontal overflow, and unnecessarily tall sections.

Use Streamlit columns and containers to establish a consistent hierarchy. Do not attempt to reproduce complex CSS layouts that break when the viewport changes.

## 6. Rebuild the Venue Visualization

This is the most important part of the rebuild.

The existing coordinate graph is visually inadequate. Replace it with a polished, interactive venue floor-plan visualization.

### A. Venue Canvas

Use Plotly to render a top-down, two-dimensional event venue.

The visualization should resemble a professional architectural floor plan rather than a mathematical graph.

Requirements:

* Remove visible numerical axes, tick labels, and unnecessary chart gridlines.
* Use a clean venue background with a subtle boundary.
* Maintain a consistent coordinate system internally, even when axes are hidden.
* Use equal scaling for the X and Y dimensions so venue geometry is not distorted.
* Use clean outlines and readable facility labels.
* Provide sufficient spacing between facilities.
* Prevent facility labels from overlapping.
* Fit the venue to the available display area.
* Preserve spatial relationships when the display size changes.

Use Plotly shapes, annotations, scatter traces, and heatmap layers as appropriate.

### B. Venue Elements

Represent the following as distinct visual objects:

* Main stage.
* Entrance and exit.
* Food zone.
* Photo zone.
* Booths.
* Main walking paths.
* Emergency access routes.
* Accessible routes.
* Rest areas.
* Toilets and other fixed facilities.

Use a restrained, consistent visual language. Each facility type should have a distinct fill, outline, and label treatment.

Represent walking paths and emergency routes using different line styles and labels.

Do not rely on color alone to communicate meaning.

Facilities should be generated from actual layout data rather than hard-coded directly into chart-rendering code.

### C. Interactive Facility Selection

Allow users to select a facility on the map and inspect its details in a dedicated information panel.

Display:

* Facility name and type.
* Position and dimensions.
* Estimated visitors.
* Estimated congestion level.
* Accessibility status.
* Relevant recommendations.

If full drag-and-drop editing is not reliably supported by the chosen Streamlit/Plotly interaction approach, implement a dependable alternative using facility selection and position/size controls.

Never present a nonfunctional drag-and-drop feature as implemented.

### D. Visualization Controls

Provide working controls to toggle:

* Facility labels.
* Visitor movement paths.
* Congestion heatmap.
* Accessibility routes.
* Emergency routes.
* Before/after comparison.

Every toggle must visibly change the visualization.

Provide a clear reset-layout action.

## 7. Crowd Simulation and Congestion Visualization

The existing visualization places many overlapping dots at the entrance. Replace this with a meaningful, interpretable simulation.

### A. Visitor Movement

Create a simplified visitor-flow simulation based on:

* Entrance and exit positions.
* Facility locations.
* Expected visitor count.
* Event duration.
* Facility attractiveness or visit demand.
* Walking-path connectivity.
* Approximate facility service capacity.

Represent movement paths using directional lines or arrows.

If individual visitor positions are animated, keep the number of visualized agents small enough to maintain responsive performance. The simulated agent count must not be misrepresented as a real-world measurement.

Provide a time-step control or a simulation timeline when feasible.

### B. Congestion Heatmap

Show estimated congestion spatially across the venue.

The heatmap should:

* Align correctly with the venue geometry.
* Use a clear low-to-high congestion scale.
* Highlight likely bottlenecks and high-density areas.
* Avoid covering facility labels with excessive opacity.
* Update when the layout or visitor assumptions change.

### C. Simulation Controls

Implement:

* Run simulation.
* Reset simulation.
* Change visitor count.
* Change event duration.
* Change relevant facility settings.
* Switch between baseline and optimized layouts.

Simulation results must be reproducible for identical inputs.

Clearly distinguish simulated estimates from observed data.

Do not claim that the model validates real-world crowd safety or predicts exact pedestrian behavior.

## 8. Event Configuration

Create a functional Event Design page.

Include these inputs:

* Event name.
* Venue type.
* Expected visitor count.
* Event duration.
* Budget in Korean won.
* Number of booths.
* Number of food facilities.
* Number of photo zones.
* Stage requirements.
* Number and location of entrances and exits where supported.
* Required fixed facilities.
* Accessibility requirements.
* Primary event objective.

Provide objective selection:

* Safety.
* Accessibility.
* Visitor experience.
* Operational efficiency.
* Budget efficiency.
* Balanced optimization.

Include sensible sample defaults for a school festival.

Validate all inputs. Prevent negative visitor counts, invalid dimensions, impossible facility placements, and invalid budget values.

Keep the configuration synchronized with the venue, simulation, and report pages.

## 9. Layout Generation and Optimization Engine

Implement a real, testable layout-generation engine.

The engine should:

1. Read the event configuration.
2. Construct a baseline venue layout.
3. Generate several valid alternative layouts.
4. Check facility boundaries and collisions.
5. Evaluate walking-path connectivity.
6. Estimate congestion and accessibility.
7. Calculate objective-specific scores.
8. Select the best candidate according to the chosen objective.
9. Return the chosen layout, its metrics, and an explanation of the selection.

Use a transparent multi-objective scoring system.

Example metrics:

* Congestion risk.
* Route connectivity.
* Accessibility coverage.
* Estimated waiting time.
* Facility spacing.
* Budget usage.
* Visitor-flow efficiency.

Normalize metric scales before combining them.

Safety-related scores must be described as planning indicators, not certified safety assessments.

The optimizer must not merely return the same layout with different labels. The selected candidate must be meaningfully different when feasible, and the score calculation must be traceable.

If no valid improvement exists, explicitly explain why.

## 10. Analysis Panel

Place a compact analysis panel beside the venue map.

Include:

* Overall planning score.
* Congestion indicator.
* Accessibility indicator.
* Flow-efficiency indicator.
* Estimated waiting time.
* Budget utilization.

For every score, provide a short explanation of what it means.

Avoid arbitrary numbers that are not connected to calculations.

If a score is displayed as a percentage, define how it is calculated and ensure that higher values consistently mean better performance. For risk metrics, clearly label whether higher or lower is better.

### AI Recommendations

Generate recommendations from actual detected issues.

Examples:

* Move the photo zone away from the entrance.
* Increase clearance around a bottleneck.
* Improve the connection between the food zone and the main circulation path.
* Provide an accessible route to the stage.
* Distribute high-demand facilities across the venue.

Each recommendation must include:

* Detected issue.
* Proposed action.
* Reason.
* Expected change in the relevant metric, when calculated.

Provide an Apply Recommendation action when the change can be implemented automatically.

After applying a recommendation, update the layout and recalculate dependent metrics.

Do not show fabricated improvement percentages.

## 11. Before-and-After Comparison

Implement a clear comparison between:

* Original layout.
* Optimized layout.

Allow users to switch between the layouts or inspect them side by side when sufficient screen space is available.

Compare:

* Overall planning score.
* Congestion.
* Estimated waiting time.
* Accessibility coverage.
* Budget utilization.

Use the same metric definitions for both layouts.

Display absolute changes and percentage changes only when mathematically appropriate.

If a value cannot be calculated, show an unavailable state rather than inventing a number.

## 12. Analytics

Create relevant charts using Plotly.

Include:

1. Estimated visitor distribution over time.
2. Facility-level congestion comparison.
3. Before-and-after metric comparison.
4. Optional estimated waiting-time comparison.

Charts must be linked to the actual simulation data and configuration.

Use concise Korean labels, consistent units, readable tooltips, and restrained colors.

Avoid unnecessary 3D charts, decorative graphs, and charts that do not support a planning decision.

## 13. AI Report

Create a functional report page that summarizes the selected event plan.

Include:

* Event configuration.
* Selected venue layout.
* Main detected risks.
* Accessibility findings.
* Optimization objective.
* Original versus optimized metrics.
* Recommendations and their calculated effects.
* Model assumptions and limitations.

Allow users to download a report in CSV or JSON format using standard Streamlit download controls. If a PDF report is implemented, verify that Korean text renders correctly.

The report must use the same underlying results as the dashboard. Do not generate a separate set of inconsistent numbers.

## 14. Visual Design System

Use a professional enterprise design language inspired by high-quality products such as Apple, Microsoft, and Figma.

Suggested visual direction:

* Deep navy or neutral dark sidebar.
* Clean white or softly tinted workspace.
* Restrained blue accent color.
* Distinct but accessible congestion colors.
* Consistent typography and spacing.
* Thin borders and subtle separators.
* Small, purposeful metric cards.
* Clear visual hierarchy.

Dark mode may be supported, but do not sacrifice readability for a dark appearance.

Avoid:

* Huge rounded cards.
* Excessive shadows and gradients.
* Oversized text.
* Large emoji as primary interface elements.
* Inconsistent spacing.
* Dense blocks of text.
* Overlapping labels.
* Exposed coordinate axes.
* A graph that occupies most of the screen without meaningful supporting analysis.

Use custom CSS only when necessary, and keep it compatible with Streamlit's layout and deployment environment.

## 15. Korean Localization

All user-facing text must be in natural Korean.

Use consistent terminology:

* 대시보드
* 행사 설계
* 디지털 트윈
* AI 시뮬레이션
* AI 분석 보고서
* 혼잡도
* 접근성
* 이동 효율
* 예상 대기시간
* 기존 배치
* 최적화 배치

Code identifiers may remain in English.

Use consistent number formatting and Korean won for budget values.

## 16. Streamlit State and Reliability

Use `st.session_state` to preserve:

* Event configuration.
* Original layout.
* Current layout.
* Selected facility.
* Simulation settings.
* Simulation results.
* Optimization results.
* Display toggles.

Avoid resetting user input every time a widget triggers a rerun.

Separate code into logical modules where appropriate, such as:

* Application entry point.
* UI components.
* Venue visualization.
* Simulation engine.
* Layout optimizer.
* Metrics and scoring.
* Report generation.
* Sample data and configuration.

Do not create excessive files for trivial functions.

Handle missing or invalid data gracefully.

Avoid unnecessary reruns and excessive chart rendering.

## 17. GitHub and Streamlit Deployment

Ensure that the project can run in the existing deployment environment.

Verify:

* The correct Streamlit entry point.
* Dependency installation.
* Relative asset paths.
* No hard-coded local machine paths.
* No secrets committed to GitHub.
* No mandatory external API calls for core functionality.
* Correct behavior after application reruns.
* Compatibility with the current Python and Streamlit versions.

Preserve necessary deployment files, such as `requirements.txt` and Streamlit configuration, when applicable.

Do not overwrite unrelated repository content.

## 18. Required Verification

After implementation:

1. Check Python syntax and import errors.
2. Run available tests.
3. Test the simulation engine independently of the UI.
4. Verify that different visitor counts produce appropriate changes in the simulation.
5. Verify that changing the event objective changes the optimization scoring or candidate selection when appropriate.
6. Verify that applying a recommendation changes the layout when applicable.
7. Verify that all charts and metrics update consistently.
8. Verify that display toggles actually work.
9. Verify that the application starts with the correct Streamlit command.
10. Fix errors discovered during testing.

Do not claim that tests passed unless they were actually executed.

## 19. Final Deliverable

Deliver a complete, runnable application in the existing GitHub repository.

Prioritize the following in order:

1. Correct application structure and successful execution.
2. Professional, readable venue visualization.
3. Functional layout generation and simulation.
4. Consistent, data-driven analytics.
5. Before-and-after comparison.
6. Responsive UI and polish.

Do not stop after generating a design mockup or writing a plan. Implement the application.

At completion, provide a concise summary of:

* Files created or changed.
* Major features implemented.
* Dependencies added or retained.
* Exact command to run the app.
* Tests actually performed and their results.
* Any remaining limitations.

**Final acceptance criterion:** The application must look and behave like a coherent event-planning tool, not a coordinate chart surrounded by cards. Changing the event conditions must produce consistent, explainable changes in the venue layout, simulation, analysis, and report.
