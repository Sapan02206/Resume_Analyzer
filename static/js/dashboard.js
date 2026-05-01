/**
 * Career Dashboard JavaScript
 * Handles data loading, UI updates, and user interactions
 */

// Global state
let dashboardData = null;
let projectsData = null;
let progressData = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadProjects();
    loadProgress();
});

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Load dashboard data from API
 */
async function loadDashboard() {
    try {
        showLoading();
        
        // Dashboard API automatically handles session data
        const response = await fetch('/dashboard');
        const data = await response.json();
        
        if (!response.ok) {
            // If error indicates no resume, redirect to home
            if (data.redirect) {
                showError('No resume found. Redirecting to homepage...');
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 2000);
                return;
            }
            throw new Error(data.error || 'Failed to load dashboard');
        }
        
        dashboardData = data;
        renderDashboard(data);
        
    } catch (error) {
        console.error('Dashboard load error:', error);
        showError('Failed to load dashboard. Redirecting to homepage...');
        
        // Redirect to home after 3 seconds
        setTimeout(() => {
            window.location.href = '/';
        }, 3000);
    } finally {
        hideLoading();
    }
}

/**
 * Render dashboard UI with data
 */
function renderDashboard(data) {
    // Update overall score
    const score = Math.round(data.readiness.overall_score);
    document.getElementById('overallScore').textContent = score;
    
    // Update score circle color
    const scoreCircle = document.getElementById('scoreCircle');
    const statusBadge = document.getElementById('statusBadge');
    const statusMessage = document.getElementById('statusMessage');
    
    let statusClass, statusText, message;
    
    if (score >= 80) {
        statusClass = 'excellent';
        statusText = '🎉 Ready to Apply!';
        message = 'You have strong qualifications for this role. Start applying with confidence!';
    } else if (score >= 60) {
        statusClass = 'good';
        statusText = '👍 Almost There';
        message = 'You\'re on the right track. Focus on the recommendations below to strengthen your profile.';
    } else if (score >= 40) {
        statusClass = 'moderate';
        statusText = '📚 Keep Learning';
        message = 'You have a foundation, but need to build more skills and experience for this role.';
    } else {
        statusClass = 'needs-work';
        statusText = '🚀 Getting Started';
        message = 'This role requires significant preparation. Follow the roadmap below to get there.';
    }
    
    scoreCircle.classList.add(`score-${statusClass}`);
    statusBadge.className = `status-badge status-${statusClass}`;
    statusBadge.textContent = statusText;
    statusMessage.textContent = message;
    
    // Update target role
    document.getElementById('targetRole').textContent = data.target_role;
    
    // Update metric cards
    document.getElementById('skillMatchScore').textContent = Math.round(data.readiness.skill_match_score);
    document.getElementById('experienceScore').textContent = Math.round(data.readiness.experience_score);
    document.getElementById('evidenceScore').textContent = Math.round(data.readiness.evidence_score);
    
    // Render skill gaps
    renderSkillGaps(data.gap_analysis);
    
    // Render matched skills
    renderMatchedSkills(data.gap_analysis);
    
    // Render recommendations
    renderRecommendations(data.recommendations);
}

/**
 * Render skill gaps section
 */
function renderSkillGaps(gapAnalysis) {
    const container = document.getElementById('missingSkills');
    
    const missingRequired = gapAnalysis.missing_required || [];
    const missingOptional = gapAnalysis.missing_optional || [];
    
    if (missingRequired.length === 0 && missingOptional.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-check-circle-fill text-success"></i>
                <p class="mb-0">Great! You have all the required skills for this role.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Missing required skills (high priority)
    if (missingRequired.length > 0) {
        html += '<h6 class="text-danger mb-3"><i class="bi bi-exclamation-circle"></i> Critical Skills to Learn</h6>';
        missingRequired.forEach(skill => {
            html += `
                <div class="skill-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${skill.skill}</strong>
                            <span class="badge-missing ms-2">Required</span>
                        </div>
                        <small class="text-muted">${skill.reason}</small>
                    </div>
                </div>
            `;
        });
    }
    
    // Missing optional skills (lower priority)
    if (missingOptional.length > 0 && missingOptional.length <= 5) {
        html += '<h6 class="text-warning mt-4 mb-3"><i class="bi bi-star"></i> Nice-to-Have Skills</h6>';
        missingOptional.slice(0, 5).forEach(skill => {
            html += `
                <div class="skill-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${skill.skill}</strong>
                            <span class="badge bg-light text-dark ms-2">Optional</span>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

/**
 * Render matched skills section
 */
function renderMatchedSkills(gapAnalysis) {
    const container = document.getElementById('matchedSkills');
    
    const matchedRequired = gapAnalysis.matched_required || [];
    
    if (matchedRequired.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-info-circle"></i>
                <p class="mb-0">No matched skills yet. Upload your resume to see your strengths.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    matchedRequired.forEach(skill => {
        const years = skill.experience_years ? `${skill.experience_years} years` : 'Experience detected';
        html += `
            <div class="skill-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${skill.skill}</strong>
                        <span class="badge-matched ms-2">✓</span>
                    </div>
                    <small class="text-muted">${years}</small>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Render recommendations section
 */
function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-check-circle-fill text-success"></i>
                <p class="mb-0">You're all set! No immediate actions needed.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    recommendations.slice(0, 5).forEach((rec, index) => {
        html += `
            <div class="recommendation-card">
                <div class="d-flex align-items-start">
                    <span class="recommendation-priority">${index + 1}</span>
                    <div class="flex-grow-1">
                        <h6 class="mb-2">${rec.title}</h6>
                        <p class="mb-2 text-muted small">${rec.description}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-light text-dark">
                                <i class="bi bi-clock"></i> ${rec.estimated_time}
                            </span>
                            <small class="text-muted">${rec.action}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Load projects from API
 */
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load projects');
        }
        
        projectsData = data;
        renderProjects(data.projects);
        
    } catch (error) {
        console.error('Projects load error:', error);
        document.getElementById('projectsList').innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> Failed to load projects
            </div>
        `;
    }
}

/**
 * Render projects list
 */
function renderProjects(projects) {
    const container = document.getElementById('projectsList');
    
    if (!projects || projects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-folder-plus"></i>
                <p class="mb-0">No projects yet. Add your first project to boost your evidence score!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    projects.forEach(project => {
        const hasUrl = project.project_url && project.project_url.trim() !== '';
        const dateRange = project.start_date && project.end_date 
            ? `${formatDate(project.start_date)} - ${formatDate(project.end_date)}`
            : 'Date not specified';
        
        html += `
            <div class="project-card">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">${project.title}</h6>
                    ${hasUrl ? `<a href="${project.project_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-box-arrow-up-right"></i>
                    </a>` : ''}
                </div>
                ${project.description ? `<p class="text-muted small mb-2">${project.description}</p>` : ''}
                <div class="project-skills">
                    ${(project.skills_used || []).map(skill => 
                        `<span class="project-skill-tag">${skill}</span>`
                    ).join('')}
                </div>
                <small class="text-muted d-block mt-2">
                    <i class="bi bi-calendar"></i> ${dateRange}
                </small>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Load progress timeline from API
 */
async function loadProgress() {
    try {
        const response = await fetch('/api/progress');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load progress');
        }
        
        progressData = data;
        renderProgress(data);
        
    } catch (error) {
        console.error('Progress load error:', error);
        document.getElementById('progressTimeline').innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> Failed to load progress
            </div>
        `;
    }
}

/**
 * Render progress timeline
 */
function renderProgress(data) {
    const container = document.getElementById('progressTimeline');
    
    if (!data.timeline || data.timeline.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-graph-up"></i>
                <p class="mb-0">Your progress will appear here as you improve your profile.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Show improvement summary
    if (data.improvement !== 0) {
        const improvementClass = data.improvement > 0 ? 'text-success' : 'text-danger';
        const improvementIcon = data.improvement > 0 ? 'arrow-up' : 'arrow-down';
        html += `
            <div class="alert alert-info mb-3">
                <strong>
                    <i class="bi bi-${improvementIcon} ${improvementClass}"></i>
                    ${data.improvement > 0 ? '+' : ''}${data.improvement} points
                </strong>
                since you started
            </div>
        `;
    }
    
    // Show timeline (most recent first)
    const timeline = [...data.timeline].reverse().slice(0, 5);
    
    timeline.forEach(point => {
        const score = Math.round(point.overall_score);
        const date = formatDate(point.date);
        
        html += `
            <div class="progress-item">
                <div class="progress-date">${date}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: ${score}%"></div>
                </div>
                <div class="progress-score">${score}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Add new project
 */
async function addProject() {
    const title = document.getElementById('projectTitle').value.trim();
    const description = document.getElementById('projectDescription').value.trim();
    const skillsInput = document.getElementById('projectSkills').value.trim();
    const startDate = document.getElementById('projectStartDate').value;
    const endDate = document.getElementById('projectEndDate').value;
    const url = document.getElementById('projectUrl').value.trim();
    
    if (!title) {
        alert('Please enter a project title');
        return;
    }
    
    // Parse skills
    const skills = skillsInput ? skillsInput.split(',').map(s => s.trim()).filter(s => s) : [];
    
    // Build request body
    const projectData = {
        title: title,
        description: description || null,
        skills_used: skills,
        start_date: startDate || null,
        end_date: endDate || null,
        project_url: url || null
    };
    
    try {
        // Show loading overlay
        showLoading();
        
        // Close modal first for better UX
        const modal = bootstrap.Modal.getInstance(document.getElementById('addProjectModal'));
        modal.hide();
        
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to add project');
        }
        
        // Clear form
        document.getElementById('addProjectForm').reset();
        
        // Show success message
        showSuccess('Project added! Your readiness score is being recalculated...');
        
        // Reload all data to get updated scores
        await Promise.all([
            loadProjects(),
            loadDashboard(),  // This will recalculate with new project
            loadProgress()
        ]);
        
        // Highlight the evidence score to show it changed
        highlightScoreChange('evidenceScore');
        highlightScoreChange('overallScore');
        
    } catch (error) {
        console.error('Add project error:', error);
        showError('Failed to add project: ' + error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Highlight score change with animation
 */
function highlightScoreChange(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.transition = 'all 0.5s ease';
        element.style.transform = 'scale(1.2)';
        element.style.color = '#10b981';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
            element.style.color = '#667eea';
        }, 500);
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Show error message with better UX
 */
function showError(message) {
    // Create toast-style notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.innerHTML = `
        <i class="bi bi-exclamation-circle me-2"></i>
        <strong>Error:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Show success message with better UX
 */
function showSuccess(message) {
    // Create toast-style notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.innerHTML = `
        <i class="bi bi-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
