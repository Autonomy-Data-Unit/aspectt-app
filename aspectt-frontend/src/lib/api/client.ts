const API_BASE = (typeof window !== 'undefined' && window.location.hostname !== 'localhost')
	? '/api'
	: 'http://localhost:8000/api';

async function fetchJson<T>(path: string): Promise<T> {
	const res = await fetch(`${API_BASE}${path}`);
	if (!res.ok) throw new Error(`API error: ${res.status}`);
	return res.json();
}

// --- Types ---

export interface Occupation {
	uk_soc_2020: number;
	title: string;
}

export interface OccupationWithZone extends Occupation {
	job_zone?: number;
	riasec_code?: string;
}

export interface OccupationDetail {
	uk_soc_2020: number;
	title: string;
	description: string;
	abilities: RatedElement[];
	skills: RatedElement[];
	knowledge: RatedElement[];
	work_activities: RatedElement[];
	work_context: RatedElement[];
	work_styles: RatedElement[];
	interests: InterestElement[];
	work_values: WorkValueElement[];
	tasks: Task[];
	technology_skills: TechSkill[];
	tools_used: ToolUsed[];
	detailed_work_activities: DetailedWorkActivity[];
	emerging_tasks: EmergingTask[];
	reported_job_titles: string[];
	insufficient_source_data?: string;
	education: EducationEntry[];
	job_zone: number;
	related_occupations: RelatedOccupation[];
	alternate_titles: string[];
	source_occupations: SourceOccupation[];
}

export interface RatedElement {
	element_id: string;
	element_name: string;
	value_IM?: number;
	value_LV?: number;
	value_DR?: number;
	value_CX?: number;
}

export interface InterestElement {
	element_id: string;
	element_name: string;
	value_OI?: number;
}

export interface WorkValueElement {
	element_id: string;
	element_name: string;
	value_EX?: number;
}

export interface Task {
	task: string;
	task_type: string;
}

export interface TechSkill {
	name: string;
	weight: number;
}

export interface ToolUsed {
	name: string;
	weight: number;
}

export interface DetailedWorkActivity {
	dwa_id: string;
	title: string;
	element_id: string;
	weight: number;
}

export interface EmergingTask {
	task: string;
	category: string;
}

export interface ToolSearchResult {
	uk_soc_2020: number;
	title: string;
	matching_tools: string[];
	match_count: number;
}

export interface EducationEntry {
	Element_Name: string;
	Scale_ID: string;
	Category: number;
	'Data Value': number;
}

export interface RelatedOccupation {
	related_uk_soc: number;
	related_uk_title: string;
	link_count: number;
}

export interface SourceOccupation {
	onet_soc: string;
	onet_title: string;
	weight: number;
}

export interface MajorGroup {
	code: number;
	title: string;
	occupation_count: number;
}

export interface JobZone {
	zone: number;
	name: string;
	label?: string;
	occupation_count: number;
	occupations: Occupation[];
}

export interface InterestSummary {
	code: string;
	name: string;
	primary_count: number;
}

export interface DescriptorElement {
	element_name: string;
	occupation_count: number;
	average_importance: number;
}

export interface DescriptorOccupation {
	uk_soc_2020: number;
	title: string;
	importance: number;
	job_zone?: number;
}

export interface CompareOccupation {
	uk_soc_2020: number;
	title: string;
	description: string;
	job_zone?: number;
	riasec_code: string;
	top_skills: RatedElement[];
	top_abilities: RatedElement[];
	top_knowledge: RatedElement[];
	top_work_activities: RatedElement[];
	top_technology_skills: TechSkill[];
	interests: InterestElement[];
	work_values: WorkValueElement[];
	task_count: number;
	tech_skill_count: number;
	top_tools_used: ToolUsed[];
	tool_count: number;
}

export interface TaskResult {
	uk_soc_2020: number;
	title: string;
	task: string;
	task_type: string;
}

export interface TechSearchResult {
	uk_soc_2020: number;
	title: string;
	matching_technologies: string[];
	match_count: number;
}

export interface TechBrowseItem {
	name: string;
	occupation_count: number;
}

export interface Stats {
	total_occupations: number;
	total_tasks: number;
	total_technology_skills: number;
	total_tools_used: number;
	soc_version: string;
	source: string;
	data_categories: string[];
}

// --- Core ---

export async function searchOccupations(q: string, limit = 50, offset = 0, jobZone?: number) {
	let url = `/occupations?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`;
	if (jobZone !== undefined) url += `&job_zone=${jobZone}`;
	return fetchJson<{ total: number; occupations: Occupation[] }>(url);
}

export async function listOccupations(params: {
	majorGroup?: number;
	jobZone?: number;
	q?: string;
	limit?: number;
	offset?: number;
} = {}) {
	const { majorGroup, jobZone, q, limit = 50, offset = 0 } = params;
	let url = `/occupations?limit=${limit}&offset=${offset}`;
	if (majorGroup !== undefined) url += `&major_group=${majorGroup}`;
	if (jobZone !== undefined) url += `&job_zone=${jobZone}`;
	if (q) url += `&q=${encodeURIComponent(q)}`;
	return fetchJson<{ total: number; occupations: Occupation[] }>(url);
}

export async function getOccupation(socCode: number) {
	return fetchJson<OccupationDetail>(`/occupations/${socCode}`);
}

// --- Browse ---

export async function getMajorGroups() {
	return fetchJson<{ major_groups: MajorGroup[] }>('/browse/major-groups');
}

export async function getJobZones() {
	return fetchJson<{ job_zones: JobZone[] }>('/browse/job-zones');
}

export async function getInterests(code?: string, jobZone?: number, limit = 100, offset = 0) {
	let url = `/browse/interests?limit=${limit}&offset=${offset}`;
	if (code) url += `&code=${encodeURIComponent(code)}`;
	if (jobZone !== undefined) url += `&job_zone=${jobZone}`;
	return fetchJson<{
		interests: InterestSummary[];
		code_filter?: string;
		total?: number;
		occupations?: OccupationWithZone[];
	}>(url);
}

export async function getDescriptors(category: string, limit = 50) {
	return fetchJson<{
		category: string;
		total: number;
		elements: DescriptorElement[];
	}>(`/browse/descriptors/${category}?limit=${limit}`);
}

export async function getDescriptorOccupations(
	category: string,
	elementName: string,
	jobZone?: number,
	limit = 100,
	offset = 0,
) {
	let url = `/browse/descriptors/${category}/${encodeURIComponent(elementName)}?limit=${limit}&offset=${offset}`;
	if (jobZone !== undefined) url += `&job_zone=${jobZone}`;
	return fetchJson<{
		category: string;
		element_name: string;
		total: number;
		occupations: DescriptorOccupation[];
	}>(url);
}

export async function getTechSkillsBrowse(q = '', limit = 100, offset = 0) {
	let url = `/browse/technology-skills?limit=${limit}&offset=${offset}`;
	if (q) url += `&q=${encodeURIComponent(q)}`;
	return fetchJson<{
		total: number;
		technology_skills: TechBrowseItem[];
	}>(url);
}

// --- Advanced Search ---

export async function searchTasks(q: string, limit = 50, offset = 0) {
	return fetchJson<{
		total: number;
		results: TaskResult[];
	}>(`/search/tasks?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`);
}

export async function searchTechSkills(q: string, limit = 50, offset = 0) {
	return fetchJson<{
		total: number;
		matching_technology_names: string[];
		results: TechSearchResult[];
	}>(`/search/technology-skills?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`);
}

export async function searchTools(q: string, limit = 50, offset = 0) {
	return fetchJson<{
		total: number;
		matching_tool_names: string[];
		results: ToolSearchResult[];
	}>(`/search/tools-used?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`);
}

export async function searchBySkill(q: string, limit = 50, offset = 0) {
	return fetchJson<{
		total: number;
		results: Array<{
			uk_soc_2020: number;
			title: string;
			skill_name: string;
			importance: number;
			level: number;
		}>;
	}>(`/search/skills?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`);
}

// --- Compare ---

export async function compareOccupations(codes: number[]) {
	return fetchJson<{
		occupations: CompareOccupation[];
	}>(`/compare?codes=${codes.join(',')}`);
}

// --- Crosswalk ---

export interface OnetOccupation {
	onet_soc: string;
	title: string;
}

export async function searchOnetOccupations(q: string, limit = 10) {
	return fetchJson<{ total: number; occupations: OnetOccupation[] }>(
		`/onet-occupations?q=${encodeURIComponent(q)}&limit=${limit}`
	);
}

export async function getCrosswalk(params: {
	ukSoc?: number;
	onetSoc?: string;
	limit?: number;
	offset?: number;
} = {}) {
	const { ukSoc, onetSoc, limit = 100, offset = 0 } = params;
	let url = `/crosswalk?limit=${limit}&offset=${offset}`;
	if (ukSoc !== undefined) url += `&uk_soc=${ukSoc}`;
	if (onetSoc) url += `&onet_soc=${encodeURIComponent(onetSoc)}`;
	return fetchJson<{
		total: number;
		crosswalk: Array<{
			onet_soc: string;
			onet_title: string;
			uk_soc_2020: number;
			uk_soc_title: string;
			weight: number;
		}>;
	}>(url);
}

// --- Stats ---

export async function getStats() {
	return fetchJson<Stats>('/stats');
}
