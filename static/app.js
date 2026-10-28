const $ = id => document.getElementById(id);
let catalogue, currentRequest, edits = {};
const labels = {project_summary:'Project understanding',objectives:'Objectives',scope_items:'Scope of work',deliverables:'Deliverables',assumptions:'Assumptions to validate',exclusions:'Exclusions',milestones:'Milestones',dependencies:'Dependencies',client_questions:'Client-confirmation questions',commercial_details:'Commercial details',discovery_evidence:'Discovery statements · unconfirmed',missing_information:'Missing information',conflicts:'Scope review'};
async function api(url, body) {
  const response = await fetch(url, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Check input lengths and required fields, then try again.');
  }
  return response;
}
function status(message) {$('status').textContent=message;}
function render(proposal) {
  edits={}; $('sections').replaceChildren();
  $('empty').hidden=true; $('result').hidden=false;
  const selectedPackage=catalogue.packages.find(p=>p.id===currentRequest.package_id);
  const selectedTemplate=catalogue.templates.find(t=>t.id===proposal.template_id);
  $('warnings').replaceChildren();
  const reviewTitle=document.createElement('strong'); reviewTitle.textContent='Your draft is ready. Before sharing:'; $('warnings').append(reviewTitle);
  const reviewList=document.createElement('ul');
  const actions=proposal.sections.missing_information.map(item=>({
    'Client name':'Add the client name.', 'Target timeline':'Agree a delivery timeline; use the planning guidance as a starting point.',
    'Client approver':'Name the person who will approve the work.', 'Approved pricing':'Add authorized pricing before sending a commercial proposal.',
    'Package recommendations need scope agreement':'Agree the recommended scope and deliverables with the client.'
  }[item] || 'Confirm: '+item));
  if(!proposal.template_approved) actions.push('Have the proposal wording reviewed before external use.');
  for(const action of actions){const li=document.createElement('li');li.textContent=action;reviewList.append(li);} $('warnings').append(reviewList);
  $('source').textContent=`${selectedPackage.name} | ${selectedTemplate.name}`;
  $('fixed').textContent=proposal.fixed_wording;
  for (const key of proposal.section_order) {
    const section=document.createElement('section'); section.className='draft-section';
    const heading=document.createElement('h3'); heading.textContent=labels[key] || key; section.append(heading);
    if (['project_summary','objectives'].includes(key)) {
      const editor=document.createElement('textarea'); editor.rows=4; editor.maxLength=5000; editor.value=proposal.sections[key].join('\n'); editor.setAttribute('aria-label',labels[key]);
      editor.addEventListener('input',()=>{edits[key]=editor.value;}); section.append(editor);
    } else {
      const list=document.createElement('ul');
      for (const text of proposal.sections[key]) {const li=document.createElement('li');li.textContent=text;list.append(li);}
      section.append(list);
    }
    $('sections').append(section);
  }
  $('amendments').value='';
}
$('draft-form').addEventListener('submit',async event=>{
  event.preventDefault(); $('generate').disabled=true; $('export').disabled=true; status('Preparing draft…');
  try {
    const request=Object.fromEntries(new FormData(event.target));
    const proposal=await (await api('/api/draft',request)).json(); currentRequest=request; render(proposal);
    $('export').disabled=false; status('Draft ready. Review the open questions and any scope conflicts.');
  } catch(error) {status(error.message);} finally {$('generate').disabled=false;}
});
$('draft-form').addEventListener('input',()=>{if(currentRequest){$('export').disabled=true;status('Inputs changed. Generate a new draft before exporting.');}});
$('notes').addEventListener('input',()=>{const count=$('notes').value.trim().split(/\s+/).filter(Boolean).length;$('brief-guidance').textContent=`${count} words. Recommended: 40-150 words describing the goal, scope, expected outputs and available inputs. Shorter briefs still work, but may need more clarification.`;});
$('sample').addEventListener('click',()=>{
  $('notes').value='The goal is to understand customer behaviour.\nClient will provide the data.\nWe need a report.\nIs the dataset ready?\nThe client also requests production deployment.';
  $('notes').dispatchEvent(new Event('input',{bubbles:true}));
});
$('export').addEventListener('click',async()=>{
  $('export').disabled=true;status('Preparing Word document…');
  try {
    const response=await api('/api/export',{request:currentRequest,reviewer_notes:$('amendments').value,edits});
    const url=URL.createObjectURL(await response.blob());const link=document.createElement('a');link.href=url;link.download='proposal-draft.docx';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    status('Draft downloaded. Resolve open questions before external use.');
  }catch(error){status(error.message);}finally{$('export').disabled=false;}
});
function describePackage(){
  const p=catalogue.packages.find(p=>p.id===$('package').value);
  $('package-description').replaceChildren();
  const description=document.createElement('span');description.textContent=p.description || 'Review the included services below.';$('package-description').append(description);
  for(const [heading,rows] of [['Suggested work',p.scope],['Expected outputs',p.deliverables]]){
    const title=document.createElement('strong');title.textContent=heading;title.style.display='block';title.style.marginTop='10px';$('package-description').append(title);
    for(const text of rows){const line=document.createElement('span');line.style.display='block';line.textContent='• '+text.replace(/^Recommended: /,'');$('package-description').append(line);}
  }
  if(p.recommended){const note=document.createElement('span');note.style.display='block';note.textContent='Planning recommendations: confirm the final inclusions with the client.';$('package-description').append(note);}
  $('timeline-guidance').textContent=p.recommended_timeline ? `Planning guide: ${p.recommended_timeline}. Adjust for project complexity, access and review time. This is a recommendation, not an agreed deadline.` : 'Agree the timeline after reviewing scope and available inputs.';
}
$('package').addEventListener('change',describePackage);
(async()=>{try{
  catalogue=await(await api('/api/catalogue')).json();
  for (const [id,rows] of [['package',catalogue.packages],['template',catalogue.templates]]) for(const row of rows){const option=document.createElement('option');option.value=row.id;option.textContent=row.sample ? `${row.name} — sample` : row.name;$(id).append(option);}
  $('template').addEventListener('change',()=>{const selected=catalogue.templates.find(t=>t.id===$('template').value);$('template-description')?.remove();const detail=document.createElement('p');detail.id='template-description';detail.className='hint';detail.textContent=[selected.purpose,selected.best_for,selected.approved?'Approved template':'Review wording before sharing'].filter(Boolean).join(' · ');$('template').after(detail);});
  $('template').dispatchEvent(new Event('change'));
  describePackage();
}catch(error){status('Unable to load the catalogue. Check that the local server is running.');$('generate').disabled=true;}})();
