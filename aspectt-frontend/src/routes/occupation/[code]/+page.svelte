<script lang="ts">
	import { page } from '$app/state';
	import { getOccupation, type OccupationDetail } from '$lib/api/client';
	import RatedBars from '$lib/components/RatedBars.svelte';

	let occ = $state<OccupationDetail | null>(null);
	let loading = $state(true);
	let error = $state('');
	let activeSection = $state('summary');

	const sections = [
		{ id: 'summary', label: 'Summary' },
		{ id: 'tasks', label: 'Tasks' },
		{ id: 'skills', label: 'Skills' },
		{ id: 'abilities', label: 'Abilities' },
		{ id: 'knowledge', label: 'Knowledge' },
		{ id: 'technology', label: 'Technology Skills' },
		{ id: 'activities', label: 'Work Activities' },
		{ id: 'context', label: 'Work Context' },
		{ id: 'styles', label: 'Work Styles' },
		{ id: 'interests', label: 'Interests' },
		{ id: 'values', label: 'Work Values' },
		{ id: 'education', label: 'Education' },
		{ id: 'related', label: 'Related Occupations' },
	];

	$effect(() => {
		const code = Number(page.params.code);
		loading = true;
		error = '';
		getOccupation(code)
			.then((data) => {
				occ = data;
				loading = false;
			})
			.catch((e) => {
				error = e.message;
				loading = false;
			});
	});

	function jobZoneLabel(jz: number): string {
		const labels: Record<number, string> = {
			1: 'Little or No Preparation Needed',
			2: 'Some Preparation Needed',
			3: 'Medium Preparation Needed',
			4: 'Considerable Preparation Needed',
			5: 'Extensive Preparation Needed',
		};
		return labels[jz] || `Zone ${jz}`;
	}
</script>

<svelte:head>
	{#if occ}
		<title>{occ.title} - ASPECTT</title>
	{/if}
</svelte:head>

<div class="container">
	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if error}
		<div class="card"><p class="error">{error}</p></div>
	{:else if occ}
		<div class="occ-header">
			<div class="occ-code">{occ.uk_soc_2020}</div>
			<div>
				<h1>{occ.title}</h1>
				<p class="occ-desc">{occ.description}</p>
			</div>
		</div>

		<div class="layout">
			<nav class="sidebar">
				{#each sections as sec}
					<button
						class="nav-item"
						class:active={activeSection === sec.id}
						onclick={() => (activeSection = sec.id)}
					>
						{sec.label}
					</button>
				{/each}
			</nav>

			<div class="content">
				{#if activeSection === 'summary'}
					<div class="card">
						<h2>Summary</h2>
						{#if occ.job_zone}
							<p class="job-zone">
								<strong>Job Zone:</strong> {occ.job_zone} — {jobZoneLabel(occ.job_zone)}
							</p>
						{/if}
						{#if occ.alternate_titles?.length}
							<div class="alt-titles">
								<strong>Also known as:</strong>
								{occ.alternate_titles.slice(0, 20).join(', ')}
								{#if occ.alternate_titles.length > 20}
									<span class="muted">and {occ.alternate_titles.length - 20} more</span>
								{/if}
							</div>
						{/if}
						{#if occ.source_occupations?.length}
							<details class="source-details">
								<summary>Based on {occ.source_occupations.length} US O*NET occupations</summary>
								<ul>
									{#each occ.source_occupations as src}
										<li>
											<span class="mono">{src.onet_soc}</span> {src.onet_title}
											<span class="muted">(weight: {src.weight.toFixed(3)})</span>
										</li>
									{/each}
								</ul>
							</details>
						{/if}
					</div>

				{:else if activeSection === 'tasks'}
					<div class="card">
						<h2>Tasks ({occ.tasks?.length ?? 0})</h2>
						{#if occ.tasks?.length}
							<ul class="task-list">
								{#each occ.tasks.slice(0, 50) as task}
									<li>
										{task.task}
										{#if task.task_type === 'Core'}
											<span class="badge">Core</span>
										{/if}
									</li>
								{/each}
							</ul>
							{#if occ.tasks.length > 50}
								<p class="muted">Showing 50 of {occ.tasks.length} tasks</p>
							{/if}
						{:else}
							<p class="muted">No task data available</p>
						{/if}
					</div>

				{:else if activeSection === 'skills'}
					<div class="card">
						<h2>Skills</h2>
						{#if occ.skills?.length}
							<RatedBars items={occ.skills} />
						{:else}
							<p class="muted">No skills data available</p>
						{/if}
					</div>

				{:else if activeSection === 'abilities'}
					<div class="card">
						<h2>Abilities</h2>
						{#if occ.abilities?.length}
							<RatedBars items={occ.abilities} />
						{:else}
							<p class="muted">No abilities data available</p>
						{/if}
					</div>

				{:else if activeSection === 'knowledge'}
					<div class="card">
						<h2>Knowledge</h2>
						{#if occ.knowledge?.length}
							<RatedBars items={occ.knowledge} />
						{:else}
							<p class="muted">No knowledge data available</p>
						{/if}
					</div>

				{:else if activeSection === 'technology'}
					<div class="card">
						<h2>Technology Skills ({occ.technology_skills?.length ?? 0})</h2>
						{#if occ.technology_skills?.length}
							<div class="tech-grid">
								{#each occ.technology_skills.slice(0, 60) as tech}
									<span class="tech-tag">{tech.name}</span>
								{/each}
							</div>
							{#if occ.technology_skills.length > 60}
								<p class="muted mt">Showing 60 of {occ.technology_skills.length} technology skills</p>
							{/if}
						{:else}
							<p class="muted">No technology skills data available</p>
						{/if}
					</div>

				{:else if activeSection === 'activities'}
					<div class="card">
						<h2>Work Activities</h2>
						{#if occ.work_activities?.length}
							<RatedBars items={occ.work_activities} />
						{:else}
							<p class="muted">No work activities data available</p>
						{/if}
					</div>

				{:else if activeSection === 'context'}
					<div class="card">
						<h2>Work Context</h2>
						{#if occ.work_context?.length}
							<RatedBars items={occ.work_context} />
						{:else}
							<p class="muted">No work context data available</p>
						{/if}
					</div>

				{:else if activeSection === 'styles'}
					<div class="card">
						<h2>Work Styles</h2>
						{#if occ.work_styles?.length}
							<RatedBars items={occ.work_styles} />
						{:else}
							<p class="muted">No work styles data available</p>
						{/if}
					</div>

				{:else if activeSection === 'interests'}
					<div class="card">
						<h2>Interests</h2>
						{#if occ.interests?.length}
							<RatedBars items={occ.interests} maxValue={7} showLevel={false} />
						{:else}
							<p class="muted">No interests data available</p>
						{/if}
					</div>

				{:else if activeSection === 'values'}
					<div class="card">
						<h2>Work Values</h2>
						{#if occ.work_values?.length}
							<RatedBars items={occ.work_values} maxValue={7} showLevel={false} />
						{:else}
							<p class="muted">No work values data available</p>
						{/if}
					</div>

				{:else if activeSection === 'education'}
					<div class="card">
						<h2>Education & Training</h2>
						{#if occ.job_zone}
							<p class="job-zone">
								<strong>Job Zone:</strong> {occ.job_zone} — {jobZoneLabel(occ.job_zone)}
							</p>
						{/if}
						{#if occ.education?.length}
							<div class="edu-list">
								{#each occ.education as edu}
									<div class="edu-row">
										<span class="edu-label">{edu.Element_Name} (Cat. {edu.Category})</span>
										<div class="bar-track">
											<div
												class="bar-fill importance"
												style="width: {Math.min(edu['Data Value'] * 10, 100)}%"
											></div>
										</div>
										<span class="bar-value">{edu['Data Value'].toFixed(1)}%</span>
									</div>
								{/each}
							</div>
						{:else}
							<p class="muted">No education data available</p>
						{/if}
					</div>

				{:else if activeSection === 'related'}
					<div class="card">
						<h2>Related Occupations</h2>
						{#if occ.related_occupations?.length}
							<div class="related-list">
								{#each occ.related_occupations as rel}
									<a class="related-item" href="/occupation/{rel.related_uk_soc}">
										<span class="related-code">{rel.related_uk_soc}</span>
										<span>{rel.related_uk_title}</span>
									</a>
								{/each}
							</div>
						{:else}
							<p class="muted">No related occupations data available</p>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.occ-header {
		display: flex;
		gap: 1.5rem;
		align-items: flex-start;
		margin-bottom: 1.5rem;
		background: var(--color-surface);
		padding: 1.5rem;
		border-radius: var(--radius);
		box-shadow: var(--shadow);
	}

	.occ-code {
		font-size: 2rem;
		font-weight: 800;
		color: var(--color-accent);
		font-family: monospace;
		flex: 0 0 auto;
		padding: 0.5rem 1rem;
		background: #ebf4ff;
		border-radius: var(--radius);
	}

	h1 {
		font-size: 1.5rem;
		color: var(--color-primary);
		margin-bottom: 0.5rem;
	}

	.occ-desc {
		color: var(--color-text-secondary);
		font-size: 0.9rem;
		line-height: 1.5;
	}

	.layout {
		display: grid;
		grid-template-columns: 200px 1fr;
		gap: 1.5rem;
	}

	.sidebar {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		position: sticky;
		top: 5rem;
		align-self: start;
	}

	.nav-item {
		display: block;
		padding: 0.5rem 0.75rem;
		background: none;
		border: none;
		border-left: 3px solid transparent;
		text-align: left;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		cursor: pointer;
		border-radius: 0 var(--radius) var(--radius) 0;
		transition: all 0.1s;
	}

	.nav-item:hover {
		background: var(--color-bg);
		color: var(--color-text);
	}

	.nav-item.active {
		border-left-color: var(--color-accent);
		background: #ebf4ff;
		color: var(--color-accent);
		font-weight: 600;
	}

	.job-zone {
		margin-bottom: 1rem;
		padding: 0.5rem 0.75rem;
		background: var(--color-bg);
		border-radius: var(--radius);
		font-size: 0.9rem;
	}

	.alt-titles {
		margin-bottom: 1rem;
		font-size: 0.9rem;
		color: var(--color-text-secondary);
		line-height: 1.8;
	}

	.source-details {
		margin-top: 1rem;
		font-size: 0.85rem;
	}

	.source-details summary {
		cursor: pointer;
		color: var(--color-accent);
		font-weight: 500;
	}

	.source-details ul {
		margin-top: 0.5rem;
		padding-left: 1.5rem;
	}

	.source-details li {
		margin-bottom: 0.25rem;
	}

	.mono {
		font-family: monospace;
		font-weight: 600;
	}

	.muted {
		color: var(--color-text-secondary);
		font-size: 0.85rem;
	}

	.mt {
		margin-top: 0.75rem;
	}

	.task-list {
		padding-left: 1.25rem;
	}

	.task-list li {
		margin-bottom: 0.5rem;
		font-size: 0.9rem;
		line-height: 1.5;
	}

	.tech-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.tech-tag {
		padding: 0.25rem 0.6rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 16px;
		font-size: 0.8rem;
	}

	.edu-list {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		margin-top: 0.5rem;
	}

	.edu-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.edu-label {
		flex: 0 0 220px;
		font-size: 0.85rem;
		text-align: right;
		color: var(--color-text-secondary);
	}

	.related-list {
		display: flex;
		flex-direction: column;
	}

	.related-item {
		display: flex;
		gap: 0.75rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid var(--color-border);
		color: var(--color-text);
	}

	.related-item:last-child {
		border-bottom: none;
	}

	.related-item:hover {
		color: var(--color-accent);
		text-decoration: none;
	}

	.related-code {
		font-family: monospace;
		font-weight: 600;
		color: var(--color-accent);
		flex: 0 0 50px;
	}

	.error {
		color: #e53e3e;
		text-align: center;
		padding: 1rem;
	}

	@media (max-width: 768px) {
		.layout {
			grid-template-columns: 1fr;
		}

		.sidebar {
			flex-direction: row;
			flex-wrap: wrap;
			position: static;
		}

		.nav-item {
			border-left: none;
			border-bottom: 2px solid transparent;
			border-radius: var(--radius);
			padding: 0.4rem 0.6rem;
			font-size: 0.8rem;
		}

		.nav-item.active {
			border-bottom-color: var(--color-accent);
		}

		.occ-header {
			flex-direction: column;
		}
	}
</style>
