shader_type canvas_item;

uniform sampler2D tex:filter_nearest;

void fragment(){
	vec2 xy=UV-vec2(.5,.5);
	float radius=sqrt(xy.x*xy.x+xy.y*xy.y);
	float angle=atan(xy.y/xy.x)+TIME;
	vec2 uv=vec2(radius*cos(angle),radius*sin(angle))+vec2(.5,.5);
	
	COLOR.rgb=vec3(.5);
	
	if(radius<.5) {COLOR.a=cos(angle);}
	if(radius>=.5){COLOR.a=0.;}
	if(radius<.3) {COLOR.a=0.;}}
