#pretreat to remove the notation
#parameter：
#          src_code
# ret      dst_code     has been solved


#for the condition with /* 123 // ,this function will output /*123 while the real output is /*123 //
# but when the output put into lex, lex will trigger the ERROR at the same line

def notation_removal(src_code):
    #remove the space and \t head and tail
    src_code=src_code.strip(" \t")
    code_len=len(src_code);
    dst_code=''
    i=0
    while(i<code_len):
        if(i<code_len-1):
            if(src_code[i]=='/' and src_code[i+1]=='/'):
                #solve the condition with //
                while(i!=code_len and src_code[i]!='\n'):
                    i+=1;
                    
            elif (src_code[i]=='/' and src_code[i+1]=='*'):
                #solve the condition with /* */
                point=i;              #use pointer to sign
                i=i+2;
                if(i==code_len):      #to prevent overflow
                    i=point;
                else:
                    while (i<=code_len-2 and not(src_code[i]=='*' and src_code[i+1]=='/')):
                        i+=1
                    if(i==code_len-1):
                        i=point      #hasn't found the */ ,use pointer to recover
                    else:
                        i+=2
        if(i<code_len):                
            dst_code+=src_code[i]
        i+=1                        

    return dst_code

def main():
    lines=[]
    while True:
        try:
            lines.append(input())
        except:                   #use ctrl+c to trigger interrupt
            break
    code='';
    for j in range (len(lines)-1):
        code+=lines[j]
        code+='\n'
    code=code.strip("\n")
    dst_code=notation_removal(code)
    print(dst_code)


main()
