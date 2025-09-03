shader_type canvas_item;

uniform sampler2D tex:filter_nearest;
uniform int height;
uniform int width;

vec2 set_pad(float x, float y){
	vec2 padding=vec2(0,0);
	if(x<y){padding=vec2(1.-x/y,0.);}
	else{   padding=vec2(0.,1.-y/x);}
	
	return(padding);}

void fragment(){
	vec2 pad=set_pad(float(height),float(width));
	vec2 uv=vec2((UV.x-pad.y/2.)/(1.-pad.y),(UV.y-pad.x/2.)/(1.-pad.x));
	
	COLOR=texture(tex,uv);
	if(uv.x<0.||uv.x>1.){COLOR.a=0.;}
	if(uv.y<0.||uv.y>1.){COLOR.a=0.;}}
